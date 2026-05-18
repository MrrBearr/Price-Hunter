import asyncio
import json
import logging
from uuid import uuid4
import redis.asyncio as redis
from app.config import get_settings
from app.database import Database

settings = get_settings()
logger = logging.getLogger(__name__)


class PriceUpdaterWorker:
    """Periodically updates prices by triggering re-scraping of stale offers."""

    def __init__(self):
        self.redis_conn = None
        self.interval = 3600  # Check every hour

    async def run(self):
        """Main loop - check for stale offers and queue re-scraping."""
        self.redis_conn = redis.from_url(settings.redis_url, decode_responses=True)
        logger.info("PriceUpdater worker started")

        while True:
            try:
                await self._check_stale_offers()
                await asyncio.sleep(self.interval)
            except Exception as e:
                logger.error(f"PriceUpdater error: {e}")
                await asyncio.sleep(30)

    async def _check_stale_offers(self):
        """Find offers not checked in last 6 hours and queue for update."""
        stale_offers = await Database.fetch(
            """
            SELECT DISTINCT p.name, p.category
            FROM offers o
            JOIN products p ON o.product_id = p.id
            WHERE o.last_checked < NOW() - INTERVAL '6 hours'
            AND o.is_available = true
            LIMIT 50
            """
        )

        if not stale_offers:
            logger.info("No stale offers found")
            return

        logger.info(f"Found {len(stale_offers)} stale product groups to update")

        for offer in stale_offers:
            task = {
                "query": offer['name'][:100],
                "stores": ["amazon", "mercadolivre", "shopee"],
            }
            await self.redis_conn.lpush("scraping_queue", json.dumps(task))

        logger.info(f"Queued {len(stale_offers)} re-scraping tasks")

    async def _record_price_history(self):
        """Record current prices to history table."""
        await Database.execute(
            """
            INSERT INTO price_history (id, offer_id, product_id, store_id, price, shipping_cost)
            SELECT uuid_generate_v4(), id, product_id, store_id, price, shipping_cost
            FROM offers
            WHERE is_available = true
            AND last_checked > NOW() - INTERVAL '1 hour'
            """
        )
        logger.info("Price history recorded")

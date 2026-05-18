import asyncio
import json
import logging
from datetime import datetime
import redis.asyncio as redis
from app.config import get_settings
from app.database import Database

settings = get_settings()
logger = logging.getLogger(__name__)


class AlertWorker:
    """Checks price alerts and triggers notifications when prices drop."""

    def __init__(self):
        self.redis_conn = None
        self.interval = 300  # Check every 5 minutes

    async def run(self):
        """Main loop - check alerts against current prices."""
        self.redis_conn = redis.from_url(settings.redis_url, decode_responses=True)
        logger.info("Alert worker started")

        while True:
            try:
                await self._check_alerts()
                await asyncio.sleep(self.interval)
            except Exception as e:
                logger.error(f"Alert worker error: {e}")
                await asyncio.sleep(30)

    async def _check_alerts(self):
        """Check all active alerts against current lowest prices."""
        alerts = await Database.fetch(
            """
            SELECT a.id, a.user_id, a.product_id, a.target_price, p.name as product_name,
                   u.email as user_email
            FROM alerts a
            JOIN products p ON a.product_id = p.id
            JOIN users u ON a.user_id = u.id
            WHERE a.is_active = true AND a.triggered = false
            """
        )

        if not alerts:
            return

        triggered_count = 0
        for alert in alerts:
            # Get current minimum price
            min_price = await Database.fetchval(
                """
                SELECT MIN(price + shipping_cost)
                FROM offers
                WHERE product_id = $1 AND is_available = true
                """,
                alert['product_id'],
            )

            if min_price is None:
                continue

            if float(min_price) <= float(alert['target_price']):
                # Trigger alert
                await Database.execute(
                    """
                    UPDATE alerts SET triggered = true, triggered_at = NOW()
                    WHERE id = $1
                    """,
                    alert['id'],
                )

                # Queue notification
                notification = {
                    "type": "price_alert",
                    "user_id": str(alert['user_id']),
                    "email": alert['user_email'],
                    "product_name": alert['product_name'],
                    "target_price": float(alert['target_price']),
                    "current_price": float(min_price),
                }
                await self.redis_conn.lpush("notification_queue", json.dumps(notification))
                triggered_count += 1

                logger.info(
                    f"Alert triggered: {alert['product_name']} "
                    f"target={alert['target_price']} current={min_price}"
                )

        if triggered_count > 0:
            logger.info(f"Triggered {triggered_count} price alerts")

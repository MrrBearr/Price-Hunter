import asyncio
import json
import logging
import redis.asyncio as redis
from app.config import get_settings
from app.scrapers import AmazonScraper, MercadoLivreScraper, ShopeeScraper
from app.product_saver import ProductSaver
from app.database import Database

settings = get_settings()
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

SCRAPERS = {
    "amazon": AmazonScraper,
    "mercadolivre": MercadoLivreScraper,
    "shopee": ShopeeScraper,
}


async def process_scraping_task(task: dict):
    """Process a single scraping task from the queue."""
    query = task.get("query", "")
    stores = task.get("stores", list(SCRAPERS.keys()))

    if not query:
        logger.warning("Empty query received, skipping")
        return

    logger.info(f"Processing scraping task: '{query}' for stores: {stores}")

    # Run scrapers concurrently with semaphore
    semaphore = asyncio.Semaphore(settings.max_concurrent_scrapers)

    async def scrape_store(store_slug: str):
        async with semaphore:
            if store_slug not in SCRAPERS:
                logger.warning(f"Unknown store: {store_slug}")
                return []

            scraper = SCRAPERS[store_slug]()
            products = await scraper.scrape_with_retry(query)
            if products:
                await ProductSaver.save_products(query, products)
            return products

    tasks = [scrape_store(store) for store in stores]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    total = sum(len(r) for r in results if isinstance(r, list))
    logger.info(f"Scraping complete for '{query}': {total} total products found")


async def main():
    """Main worker loop - listens to Redis queue."""
    logger.info("Scraper worker starting...")

    redis_conn = redis.from_url(settings.redis_url, decode_responses=True)

    # Wait for Redis
    for i in range(30):
        try:
            await redis_conn.ping()
            break
        except Exception:
            logger.info(f"Waiting for Redis... ({i + 1}/30)")
            await asyncio.sleep(2)

    logger.info("Scraper worker connected to Redis, listening for tasks...")

    while True:
        try:
            # Block and wait for task
            result = await redis_conn.brpop("scraping_queue", timeout=30)
            if result:
                _, data = result
                task = json.loads(data)
                await process_scraping_task(task)
        except redis.ConnectionError:
            logger.error("Redis connection lost, reconnecting...")
            await asyncio.sleep(5)
        except Exception as e:
            logger.error(f"Error processing task: {e}")
            await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())

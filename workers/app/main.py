import asyncio
import logging
import redis.asyncio as redis
from app.config import get_settings
from app.workers.price_updater import PriceUpdaterWorker
from app.workers.alert_worker import AlertWorker
from app.workers.coupon_tester import CouponTesterWorker

settings = get_settings()
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


async def main():
    """Main entry point - runs all workers concurrently."""
    logger.info("Workers starting...")

    # Wait for Redis
    redis_conn = redis.from_url(settings.redis_url, decode_responses=True)
    for i in range(30):
        try:
            await redis_conn.ping()
            break
        except Exception:
            logger.info(f"Waiting for Redis... ({i + 1}/30)")
            await asyncio.sleep(2)

    logger.info("Workers connected to Redis, starting worker tasks...")

    # Run all workers
    workers = [
        PriceUpdaterWorker().run(),
        AlertWorker().run(),
        CouponTesterWorker().run(),
    ]

    await asyncio.gather(*workers, return_exceptions=True)


if __name__ == "__main__":
    asyncio.run(main())

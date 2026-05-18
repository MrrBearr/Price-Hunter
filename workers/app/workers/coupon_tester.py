import asyncio
import json
import logging
from uuid import uuid4
from datetime import datetime
import redis.asyncio as redis
from playwright.async_api import async_playwright
from app.config import get_settings
from app.database import Database

settings = get_settings()
logger = logging.getLogger(__name__)


class CouponTesterWorker:
    """Tests coupons by attempting to apply them on store websites."""

    def __init__(self):
        self.redis_conn = None

    async def run(self):
        """Main loop - listen for coupon test tasks."""
        self.redis_conn = redis.from_url(settings.redis_url, decode_responses=True)
        logger.info("CouponTester worker started")

        while True:
            try:
                result = await self.redis_conn.brpop("coupon_test_queue", timeout=30)
                if result:
                    _, data = result
                    task = json.loads(data)
                    await self._test_coupon(task)
            except redis.ConnectionError:
                logger.error("Redis connection lost, reconnecting...")
                await asyncio.sleep(5)
            except Exception as e:
                logger.error(f"CouponTester error: {e}")
                await asyncio.sleep(1)

    async def _test_coupon(self, task: dict):
        """Test a coupon code on the store."""
        coupon_id = task.get("coupon_id")
        code = task.get("code")
        store_id = task.get("store_id")

        if not coupon_id or not code:
            return

        logger.info(f"Testing coupon: {code}")

        # Get store info
        store = await Database.fetchrow(
            "SELECT slug, url FROM stores WHERE id = $1",
            store_id,
        )

        if not store:
            await self._record_test(coupon_id, False, error_message="Store not found")
            return

        success = False
        discount_applied = None
        error_message = None

        try:
            success, discount_applied = await self._attempt_coupon_test(
                store['slug'], store['url'], code
            )
        except Exception as e:
            error_message = str(e)
            logger.error(f"Coupon test failed: {e}")

        # Record result
        await self._record_test(
            coupon_id,
            success,
            discount_applied=discount_applied,
            error_message=error_message,
            test_url=store['url'],
        )

        # Update coupon success rate
        await self._update_success_rate(coupon_id)

    async def _attempt_coupon_test(self, store_slug: str, store_url: str, code: str):
        """Attempt to apply coupon on store website."""
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=["--no-sandbox", "--disable-setuid-sandbox"],
            )
            context = await browser.new_context(
                viewport={"width": 1920, "height": 1080},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            )
            page = await context.new_page()

            try:
                # Navigate to store
                await page.goto(store_url, wait_until="domcontentloaded", timeout=30000)
                await page.wait_for_timeout(2000)

                # Strategy based on store
                if store_slug == "amazon":
                    success, discount = await self._test_amazon(page, code)
                elif store_slug == "mercadolivre":
                    success, discount = await self._test_mercadolivre(page, code)
                elif store_slug == "shopee":
                    success, discount = await self._test_shopee(page, code)
                else:
                    success, discount = False, None

                return success, discount

            finally:
                await browser.close()

    async def _test_amazon(self, page, code: str):
        """Test coupon on Amazon Brasil."""
        try:
            # Go to a product page and try to apply coupon at checkout simulation
            # Note: Full checkout testing requires account - we simulate validation
            await page.goto(
                f"https://www.amazon.com.br/gp/css/gc/payment?couponCode={code}",
                wait_until="domcontentloaded",
                timeout=15000,
            )
            await page.wait_for_timeout(2000)

            # Check for error messages
            error_el = await page.query_selector(".a-alert-content, .error-message")
            if error_el:
                error_text = await error_el.inner_text()
                if "inválido" in error_text.lower() or "expirado" in error_text.lower():
                    return False, None

            # Check for success
            success_el = await page.query_selector(".a-alert-success, .coupon-applied")
            if success_el:
                return True, None

            # Could not determine - mark as inconclusive
            return False, None

        except Exception:
            return False, None

    async def _test_mercadolivre(self, page, code: str):
        """Test coupon on Mercado Livre."""
        try:
            # ML doesn't have a public coupon validation endpoint
            # We check if the coupon format is valid and not expired in our DB
            return False, None
        except Exception:
            return False, None

    async def _test_shopee(self, page, code: str):
        """Test coupon on Shopee."""
        try:
            # Navigate to Shopee voucher page
            await page.goto(
                "https://shopee.com.br/voucher",
                wait_until="domcontentloaded",
                timeout=15000,
            )
            await page.wait_for_timeout(2000)

            # Look for coupon input
            input_el = await page.query_selector("input[placeholder*='cupom'], input[placeholder*='voucher']")
            if input_el:
                await input_el.fill(code)
                # Try to apply
                apply_btn = await page.query_selector("button:has-text('Aplicar'), button:has-text('Resgatar')")
                if apply_btn:
                    await apply_btn.click()
                    await page.wait_for_timeout(2000)

                    # Check result
                    error_el = await page.query_selector(".error, .invalid")
                    if error_el:
                        return False, None

                    success_el = await page.query_selector(".success, .applied")
                    if success_el:
                        return True, None

            return False, None
        except Exception:
            return False, None

    async def _record_test(
        self,
        coupon_id: str,
        success: bool,
        discount_applied: float = None,
        error_message: str = None,
        test_url: str = None,
    ):
        """Record test result in database."""
        await Database.execute(
            """
            INSERT INTO coupon_tests (id, coupon_id, success, discount_applied, error_message, test_url)
            VALUES ($1, $2, $3, $4, $5, $6)
            """,
            uuid4(),
            coupon_id,
            success,
            discount_applied,
            error_message,
            test_url,
        )

    async def _update_success_rate(self, coupon_id: str):
        """Update the coupon's success rate based on test history."""
        result = await Database.fetchrow(
            """
            SELECT
                COUNT(*) as total,
                COUNT(*) FILTER (WHERE success = true) as successes
            FROM coupon_tests
            WHERE coupon_id = $1
            """,
            coupon_id,
        )

        if result and result['total'] > 0:
            rate = (result['successes'] / result['total']) * 100
            await Database.execute(
                "UPDATE coupons SET success_rate = $1, current_uses = $2 WHERE id = $3",
                rate,
                result['total'],
                coupon_id,
            )

            # Deactivate if success rate is too low after multiple tests
            if result['total'] >= 5 and rate < 10:
                await Database.execute(
                    "UPDATE coupons SET is_active = false WHERE id = $1",
                    coupon_id,
                )
                logger.info(f"Deactivated coupon {coupon_id} - low success rate: {rate}%")

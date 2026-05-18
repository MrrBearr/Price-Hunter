import logging
import re
from typing import List
from playwright.async_api import Page
from app.base_scraper import BaseScraper, ScrapedProduct

logger = logging.getLogger(__name__)


class AmazonScraper(BaseScraper):
    BASE_URL = "https://www.amazon.com.br"

    @property
    def store_slug(self) -> str:
        return "amazon"

    @property
    def store_name(self) -> str:
        return "Amazon Brasil"

    def _parse_price(self, price_text: str) -> float:
        """Parse Brazilian price format to float."""
        if not price_text:
            return 0.0
        # Remove R$, spaces, dots (thousand sep) and convert comma to dot
        cleaned = re.sub(r'[R$\s.]', '', price_text).replace(',', '.')
        try:
            return float(cleaned)
        except (ValueError, TypeError):
            return 0.0

    async def scrape(self, query: str) -> List[ScrapedProduct]:
        """Scrape Amazon Brasil search results."""
        products = []
        page = await self.new_page()

        try:
            search_url = f"{self.BASE_URL}/s?k={query.replace(' ', '+')}"
            success = await self.safe_navigate(page, search_url)
            if not success:
                return products

            # Wait for results
            await page.wait_for_selector('[data-component-type="s-search-result"]', timeout=15000)

            # Get product cards
            cards = await page.query_selector_all('[data-component-type="s-search-result"]')

            for card in cards[:20]:  # Limit to 20 results
                try:
                    product = await self._extract_product(card, page)
                    if product and product.price > 0:
                        products.append(product)
                except Exception as e:
                    logger.warning(f"Failed to extract product: {e}")
                    continue

        except Exception as e:
            logger.error(f"Amazon scraping failed: {e}")
        finally:
            await page.close()

        logger.info(f"Amazon: found {len(products)} products for '{query}'")
        return products

    async def _extract_product(self, card, page: Page) -> ScrapedProduct:
        """Extract product data from a search result card."""
        # Product name
        name_el = await card.query_selector("h2 a span")
        name = await name_el.inner_text() if name_el else ""
        if not name:
            return None

        # Product URL
        link_el = await card.query_selector("h2 a")
        url = ""
        if link_el:
            href = await link_el.get_attribute("href")
            url = f"{self.BASE_URL}{href}" if href and not href.startswith("http") else href or ""

        # Price - whole part
        price = 0.0
        price_whole = await card.query_selector(".a-price-whole")
        price_fraction = await card.query_selector(".a-price-fraction")
        if price_whole:
            whole_text = await price_whole.inner_text()
            fraction_text = await price_fraction.inner_text() if price_fraction else "00"
            whole_clean = re.sub(r'[^\d]', '', whole_text)
            fraction_clean = re.sub(r'[^\d]', '', fraction_text)
            try:
                price = float(f"{whole_clean}.{fraction_clean}")
            except ValueError:
                price = 0.0

        # Original price (strike-through)
        original_price = None
        original_el = await card.query_selector(".a-price.a-text-price .a-offscreen")
        if original_el:
            orig_text = await original_el.inner_text()
            original_price = self._parse_price(orig_text)

        # Image
        image_url = None
        img_el = await card.query_selector("img.s-image")
        if img_el:
            image_url = await img_el.get_attribute("src")

        # Shipping
        shipping_cost = 0.0
        shipping_time = None
        delivery_el = await card.query_selector('[data-cy="delivery-recipe"] .a-color-base')
        if delivery_el:
            delivery_text = await delivery_el.inner_text()
            if "grátis" in delivery_text.lower() or "frete grátis" in delivery_text.lower():
                shipping_cost = 0.0
            shipping_time = delivery_text.strip()

        # Seller rating
        seller_rating = None
        rating_el = await card.query_selector(".a-icon-star-small .a-icon-alt")
        if rating_el:
            rating_text = await rating_el.inner_text()
            match = re.search(r'(\d[.,]\d)', rating_text)
            if match:
                seller_rating = float(match.group(1).replace(',', '.'))

        return ScrapedProduct(
            name=name.strip(),
            price=price,
            original_price=original_price,
            shipping_cost=shipping_cost,
            shipping_time=shipping_time,
            url=url,
            image_url=image_url,
            seller_name="Amazon",
            seller_rating=seller_rating,
            store_slug=self.store_slug,
        )

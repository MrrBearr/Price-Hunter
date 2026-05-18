import logging
import re
from typing import List
from playwright.async_api import Page
from app.base_scraper import BaseScraper, ScrapedProduct

logger = logging.getLogger(__name__)


class ShopeeScraper(BaseScraper):
    BASE_URL = "https://shopee.com.br"

    @property
    def store_slug(self) -> str:
        return "shopee"

    @property
    def store_name(self) -> str:
        return "Shopee"

    def _parse_price(self, price_text: str) -> float:
        """Parse Brazilian price format to float."""
        if not price_text:
            return 0.0
        cleaned = re.sub(r'[R$\s.]', '', price_text).replace(',', '.')
        try:
            return float(cleaned)
        except (ValueError, TypeError):
            return 0.0

    async def scrape(self, query: str) -> List[ScrapedProduct]:
        """Scrape Shopee search results."""
        products = []
        page = await self.new_page()

        try:
            search_url = f"{self.BASE_URL}/search?keyword={query.replace(' ', '%20')}"
            success = await self.safe_navigate(page, search_url, wait_until="networkidle")
            if not success:
                return products

            # Shopee loads dynamically - wait for content
            await page.wait_for_timeout(3000)

            # Try to find product cards
            cards = await page.query_selector_all('[data-sqe="item"]')
            if not cards:
                # Alternative selector
                cards = await page.query_selector_all(".shopee-search-item-result__item")

            for card in cards[:20]:
                try:
                    product = await self._extract_product(card)
                    if product and product.price > 0:
                        products.append(product)
                except Exception as e:
                    logger.warning(f"Failed to extract Shopee product: {e}")
                    continue

        except Exception as e:
            logger.error(f"Shopee scraping failed: {e}")
        finally:
            await page.close()

        logger.info(f"Shopee: found {len(products)} products for '{query}'")
        return products

    async def _extract_product(self, card) -> ScrapedProduct:
        """Extract product data from a search result card."""
        # Product name
        name_el = await card.query_selector("[data-sqe='name']")
        if not name_el:
            name_el = await card.query_selector(".ie3A\\+n, .Cve6sh")
        name = await name_el.inner_text() if name_el else ""
        if not name:
            # Try getting text from any child div
            all_text = await card.inner_text()
            lines = [l.strip() for l in all_text.split('\n') if l.strip()]
            name = lines[0] if lines else ""

        if not name:
            return None

        # Product URL
        link_el = await card.query_selector("a")
        url = ""
        if link_el:
            href = await link_el.get_attribute("href")
            if href:
                url = f"{self.BASE_URL}{href}" if not href.startswith("http") else href

        # Price
        price = 0.0
        price_el = await card.query_selector("[data-sqe='price']")
        if not price_el:
            price_el = await card.query_selector(".aBrP0s, .vioxXd")
        if price_el:
            price_text = await price_el.inner_text()
            # Handle price ranges (take lowest)
            prices = re.findall(r'[\d.,]+', price_text.replace('.', '').replace(',', '.'))
            if prices:
                try:
                    price = float(prices[0])
                except ValueError:
                    price = 0.0

        # Image
        image_url = None
        img_el = await card.query_selector("img")
        if img_el:
            image_url = await img_el.get_attribute("src")

        # Shipping - Shopee usually has free shipping badge
        shipping_cost = 0.0
        shipping_time = None
        free_ship_el = await card.query_selector("[data-sqe='free_shipping']")
        if not free_ship_el:
            free_ship_el = await card.query_selector(".shopee-badge-icon")
        if free_ship_el:
            shipping_cost = 0.0
            shipping_time = "Frete Grátis"

        # Seller rating
        seller_rating = None
        rating_el = await card.query_selector(".shopee-rating-stars__star-wrapper")
        if rating_el:
            seller_rating = 4.5  # Default for visible ratings

        # Sold count as proxy for reputation
        sold_el = await card.query_selector(".r6HknA, .OwmBnn")
        seller_name = "Shopee"

        return ScrapedProduct(
            name=name.strip(),
            price=price,
            original_price=None,
            shipping_cost=shipping_cost,
            shipping_time=shipping_time,
            url=url,
            image_url=image_url,
            seller_name=seller_name,
            seller_rating=seller_rating,
            store_slug=self.store_slug,
        )

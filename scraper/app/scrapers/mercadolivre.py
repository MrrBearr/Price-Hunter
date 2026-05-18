import logging
import re
from typing import List
from playwright.async_api import Page
from app.base_scraper import BaseScraper, ScrapedProduct

logger = logging.getLogger(__name__)


class MercadoLivreScraper(BaseScraper):
    BASE_URL = "https://www.mercadolivre.com.br"

    @property
    def store_slug(self) -> str:
        return "mercadolivre"

    @property
    def store_name(self) -> str:
        return "Mercado Livre"

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
        """Scrape Mercado Livre search results."""
        products = []
        page = await self.new_page()

        try:
            search_url = f"{self.BASE_URL}/jm/search?as_word={query.replace(' ', '+')}"
            success = await self.safe_navigate(page, search_url)
            if not success:
                return products

            # Wait for results
            await page.wait_for_selector(".ui-search-results", timeout=15000)

            # Get product cards
            cards = await page.query_selector_all(".ui-search-result__wrapper")

            for card in cards[:20]:
                try:
                    product = await self._extract_product(card)
                    if product and product.price > 0:
                        products.append(product)
                except Exception as e:
                    logger.warning(f"Failed to extract ML product: {e}")
                    continue

        except Exception as e:
            logger.error(f"Mercado Livre scraping failed: {e}")
        finally:
            await page.close()

        logger.info(f"Mercado Livre: found {len(products)} products for '{query}'")
        return products

    async def _extract_product(self, card) -> ScrapedProduct:
        """Extract product data from a search result card."""
        # Product name
        name_el = await card.query_selector(".ui-search-item__title")
        name = await name_el.inner_text() if name_el else ""
        if not name:
            return None

        # Product URL
        link_el = await card.query_selector("a.ui-search-link")
        url = ""
        if link_el:
            url = await link_el.get_attribute("href") or ""

        # Price
        price = 0.0
        price_el = await card.query_selector(".andes-money-amount__fraction")
        if price_el:
            price_text = await price_el.inner_text()
            price_clean = re.sub(r'[^\d]', '', price_text)
            try:
                price = float(price_clean)
            except ValueError:
                price = 0.0

        # Cents
        cents_el = await card.query_selector(".andes-money-amount__cents")
        if cents_el:
            cents_text = await cents_el.inner_text()
            cents_clean = re.sub(r'[^\d]', '', cents_text)
            try:
                price += float(cents_clean) / 100
            except ValueError:
                pass

        # Original price
        original_price = None
        orig_el = await card.query_selector(
            ".ui-search-price__second-line .andes-money-amount__fraction"
        )
        if orig_el:
            orig_text = await orig_el.inner_text()
            orig_clean = re.sub(r'[^\d]', '', orig_text)
            try:
                original_price = float(orig_clean)
            except ValueError:
                original_price = None

        # Image
        image_url = None
        img_el = await card.query_selector("img.ui-search-result-image__element")
        if img_el:
            image_url = await img_el.get_attribute("src")

        # Shipping
        shipping_cost = 0.0
        shipping_time = None
        shipping_el = await card.query_selector(".ui-search-item__shipping")
        if shipping_el:
            shipping_text = await shipping_el.inner_text()
            if "grátis" in shipping_text.lower():
                shipping_cost = 0.0
            shipping_time = shipping_text.strip()

        # Seller
        seller_name = None
        seller_el = await card.query_selector(".ui-search-official-store-label")
        if seller_el:
            seller_name = await seller_el.inner_text()

        return ScrapedProduct(
            name=name.strip(),
            price=price,
            original_price=original_price,
            shipping_cost=shipping_cost,
            shipping_time=shipping_time,
            url=url,
            image_url=image_url,
            seller_name=seller_name or "Mercado Livre",
            seller_rating=None,
            store_slug=self.store_slug,
        )

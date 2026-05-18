"""
Direct product search service using HTTP requests.
Works without Playwright/Redis - suitable for serverless (Vercel).
Uses Mercado Livre public API for real product data.
Can return results even without database connection.
"""
import re
import logging
from typing import List, Optional
from dataclasses import dataclass, asdict
from uuid import uuid4
from datetime import datetime
import httpx

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Accept-Language": "pt-BR,pt;q=0.9",
}


@dataclass
class DirectSearchResult:
    """Result that can be returned directly without DB."""
    id: str
    name: str
    slug: str
    description: Optional[str]
    category: Optional[str]
    brand: Optional[str]
    image_url: Optional[str]
    min_price: Optional[float]
    max_price: Optional[float]
    offers_count: int
    created_at: str
    # Offer details
    price: float
    original_price: Optional[float]
    shipping_cost: float
    shipping_time: Optional[str]
    url: str
    seller_name: Optional[str]
    store_name: str
    store_slug: str


def slugify(text: str) -> str:
    """Create URL slug from text."""
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_-]+', '-', text)
    return text[:250]


async def search_mercadolivre_direct(query: str) -> List[DirectSearchResult]:
    """Search Mercado Livre API and return results directly (no DB needed)."""
    results = []
    try:
        async with httpx.AsyncClient(timeout=20, headers=HEADERS) as client:
            encoded_query = query.replace(" ", "+")
            url = f"https://api.mercadolibre.com/sites/MLB/search?q={encoded_query}&limit=20"
            
            logger.info(f"Calling ML API: {url}")
            response = await client.get(url)
            logger.info(f"ML API response status: {response.status_code}")

            if response.status_code != 200:
                logger.error(f"ML API error: {response.status_code} - {response.text[:500]}")
                return results

            data = response.json()
            items = data.get("results", [])
            logger.info(f"ML API returned {len(items)} items")

            for item in items:
                price = item.get("price", 0) or 0
                if price <= 0:
                    continue

                original_price = item.get("original_price")
                shipping_cost = 0.0
                shipping_time = None

                shipping = item.get("shipping", {})
                if shipping.get("free_shipping"):
                    shipping_time = "Frete Gratis"

                image_url = item.get("thumbnail", "")
                if image_url:
                    image_url = image_url.replace("http://", "https://")
                    image_url = image_url.replace("-I.jpg", "-O.jpg")

                seller = item.get("seller", {})
                seller_name = seller.get("nickname", "Mercado Livre")
                permalink = item.get("permalink", "")
                title = item.get("title", "").strip()

                if not title:
                    continue

                results.append(DirectSearchResult(
                    id=item.get("id", str(uuid4())),
                    name=title,
                    slug=slugify(title),
                    description=None,
                    category=query,
                    brand=None,
                    image_url=image_url,
                    min_price=float(price),
                    max_price=float(price),
                    offers_count=1,
                    created_at=datetime.utcnow().isoformat(),
                    price=float(price),
                    original_price=float(original_price) if original_price and original_price != price else None,
                    shipping_cost=shipping_cost,
                    shipping_time=shipping_time,
                    url=permalink,
                    seller_name=seller_name,
                    store_name="Mercado Livre",
                    store_slug="mercadolivre",
                ))

    except httpx.TimeoutException:
        logger.error(f"ML API timeout for: {query}")
    except Exception as e:
        logger.error(f"ML search failed: {type(e).__name__}: {e}")

    return results

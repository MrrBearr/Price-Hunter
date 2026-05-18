"""
Direct product search service using HTTP requests.
Works without Playwright/Redis - suitable for serverless (Vercel).
Scrapes public APIs and search endpoints of stores.
"""
import re
import logging
import asyncio
from typing import List, Optional
from dataclasses import dataclass
import httpx
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.product import Product
from app.models.offer import Offer
from app.models.store import Store

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/html, */*",
    "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
}


@dataclass
class SearchResult:
    name: str
    price: float
    original_price: Optional[float] = None
    shipping_cost: float = 0.0
    shipping_time: Optional[str] = None
    url: str = ""
    image_url: Optional[str] = None
    seller_name: Optional[str] = None
    seller_rating: Optional[float] = None
    store_slug: str = ""


async def search_mercadolivre(query: str) -> List[SearchResult]:
    """Search Mercado Livre using their public API."""
    results = []
    try:
        async with httpx.AsyncClient(timeout=15, headers=HEADERS) as client:
            url = f"https://api.mercadolibre.com/sites/MLB/search?q={query}&limit=20"
            response = await client.get(url)
            if response.status_code != 200:
                return results

            data = response.json()
            for item in data.get("results", [])[:20]:
                price = item.get("price", 0)
                original_price = item.get("original_price")
                shipping_cost = 0.0
                shipping_time = None

                shipping = item.get("shipping", {})
                if shipping.get("free_shipping"):
                    shipping_cost = 0.0
                    shipping_time = "Frete Gratis"

                image_url = item.get("thumbnail", "").replace("http://", "https://")

                seller = item.get("seller", {})
                seller_name = seller.get("nickname", "Mercado Livre")

                results.append(SearchResult(
                    name=item.get("title", ""),
                    price=price,
                    original_price=original_price if original_price and original_price != price else None,
                    shipping_cost=shipping_cost,
                    shipping_time=shipping_time,
                    url=item.get("permalink", ""),
                    image_url=image_url,
                    seller_name=seller_name,
                    seller_rating=None,
                    store_slug="mercadolivre",
                ))
    except Exception as e:
        logger.error(f"Mercado Livre search failed: {e}")

    return results


async def search_amazon(query: str) -> List[SearchResult]:
    """Search Amazon Brasil via their search suggestions/scrape approach."""
    results = []
    try:
        async with httpx.AsyncClient(timeout=15, headers=HEADERS, follow_redirects=True) as client:
            # Use Amazon's autocomplete API for basic results
            url = f"https://completion.amazon.com.br/api/2017/suggestions?mid=A2Q3Y263D00KWC&alias=aps&prefix={query}"
            response = await client.get(url)
            if response.status_code == 200:
                data = response.json()
                suggestions = data.get("suggestions", [])
                # This gives suggestions, not full products - we'll use ML as primary
    except Exception as e:
        logger.error(f"Amazon search failed: {e}")

    return results


def slugify(text: str) -> str:
    """Create URL slug from text."""
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_-]+', '-', text)
    return text[:300]


async def search_and_save(query: str, db: AsyncSession) -> List[Product]:
    """
    Search products from external APIs and save to database.
    Returns list of Product objects.
    """
    # Search in parallel
    ml_results = await search_mercadolivre(query)
    all_results = ml_results

    if not all_results:
        return []

    # Get or create store references
    stores_cache = {}
    for slug in ["mercadolivre", "amazon", "shopee"]:
        result = await db.execute(select(Store).where(Store.slug == slug))
        store = result.scalar_one_or_none()
        if store:
            stores_cache[slug] = store

    saved_products = []

    for item in all_results:
        if item.price <= 0:
            continue

        store = stores_cache.get(item.store_slug)
        if not store:
            continue

        slug = slugify(item.name)

        # Check if product exists
        result = await db.execute(select(Product).where(Product.slug == slug))
        product = result.scalar_one_or_none()

        if not product:
            product = Product(
                name=item.name[:500],
                slug=slug,
                category=query,
                image_url=item.image_url,
            )
            db.add(product)
            await db.flush()

        # Check if offer exists
        result = await db.execute(
            select(Offer).where(
                Offer.product_id == product.id,
                Offer.store_id == store.id,
                Offer.url == item.url[:1000],
            )
        )
        existing_offer = result.scalar_one_or_none()

        if existing_offer:
            existing_offer.price = item.price
            existing_offer.original_price = item.original_price
            existing_offer.shipping_cost = item.shipping_cost
            existing_offer.shipping_time = item.shipping_time
            existing_offer.seller_name = item.seller_name
            existing_offer.is_available = True
        else:
            offer = Offer(
                product_id=product.id,
                store_id=store.id,
                price=item.price,
                original_price=item.original_price,
                shipping_cost=item.shipping_cost,
                shipping_time=item.shipping_time,
                url=item.url[:1000],
                seller_name=item.seller_name,
                seller_rating=item.seller_rating,
                is_available=True,
                score=7.0,  # Default score
            )
            db.add(offer)

        saved_products.append(product)

    await db.flush()
    return saved_products

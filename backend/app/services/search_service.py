"""
Direct product search service using HTTP requests.
Works without Playwright/Redis - suitable for serverless (Vercel).
Uses Mercado Livre public API for real product data.
"""
import re
import logging
from typing import List, Optional
from dataclasses import dataclass
import httpx

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text

from app.models.product import Product
from app.models.offer import Offer
from app.models.store import Store

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Accept-Language": "pt-BR,pt;q=0.9",
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
        async with httpx.AsyncClient(timeout=20, headers=HEADERS) as client:
            encoded_query = query.replace(" ", "%20")
            url = f"https://api.mercadolibre.com/sites/MLB/search?q={encoded_query}&limit=20"
            response = await client.get(url)

            logger.info(f"ML API status: {response.status_code} for query: {query}")

            if response.status_code != 200:
                logger.error(f"ML API returned {response.status_code}: {response.text[:200]}")
                return results

            data = response.json()
            items = data.get("results", [])
            logger.info(f"ML API returned {len(items)} results")

            for item in items[:20]:
                price = item.get("price", 0) or 0
                if price <= 0:
                    continue

                original_price = item.get("original_price")
                shipping_cost = 0.0
                shipping_time = None

                shipping = item.get("shipping", {})
                if shipping.get("free_shipping"):
                    shipping_cost = 0.0
                    shipping_time = "Frete Gratis"

                image_url = item.get("thumbnail", "")
                if image_url:
                    image_url = image_url.replace("http://", "https://")
                    # Get higher resolution image
                    image_url = image_url.replace("-I.jpg", "-O.jpg")

                seller = item.get("seller", {})
                seller_name = seller.get("nickname", "Mercado Livre")

                permalink = item.get("permalink", "")

                results.append(SearchResult(
                    name=item.get("title", "").strip(),
                    price=float(price),
                    original_price=float(original_price) if original_price and original_price != price else None,
                    shipping_cost=shipping_cost,
                    shipping_time=shipping_time,
                    url=permalink,
                    image_url=image_url,
                    seller_name=seller_name,
                    seller_rating=None,
                    store_slug="mercadolivre",
                ))
    except httpx.TimeoutException:
        logger.error(f"ML API timeout for query: {query}")
    except Exception as e:
        logger.error(f"Mercado Livre search failed: {type(e).__name__}: {e}")

    return results


def slugify(text: str) -> str:
    """Create URL slug from text."""
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_-]+', '-', text)
    return text[:250]


async def ensure_stores_exist(db: AsyncSession) -> dict:
    """Ensure default stores exist in the database, return slug->store mapping."""
    stores_cache = {}

    default_stores = [
        {"name": "Mercado Livre", "slug": "mercadolivre", "url": "https://www.mercadolivre.com.br", "reputation_score": 0.90},
        {"name": "Amazon Brasil", "slug": "amazon", "url": "https://www.amazon.com.br", "reputation_score": 0.95},
        {"name": "Shopee", "slug": "shopee", "url": "https://shopee.com.br", "reputation_score": 0.80},
    ]

    for store_data in default_stores:
        result = await db.execute(select(Store).where(Store.slug == store_data["slug"]))
        store = result.scalar_one_or_none()

        if not store:
            store = Store(
                name=store_data["name"],
                slug=store_data["slug"],
                url=store_data["url"],
                reputation_score=store_data["reputation_score"],
                is_active=True,
            )
            db.add(store)
            await db.flush()

        stores_cache[store_data["slug"]] = store

    return stores_cache


async def search_and_save(query: str, db: AsyncSession) -> List[Product]:
    """
    Search products from external APIs and save to database.
    Returns list of Product objects.
    """
    logger.info(f"search_and_save called with query: {query}")

    # Search Mercado Livre
    ml_results = await search_mercadolivre(query)
    logger.info(f"Got {len(ml_results)} results from ML API")

    if not ml_results:
        return []

    # Ensure stores exist
    stores_cache = await ensure_stores_exist(db)

    saved_products = []

    for item in ml_results:
        if item.price <= 0:
            continue

        store = stores_cache.get(item.store_slug)
        if not store:
            continue

        slug = slugify(item.name)
        if not slug:
            continue

        try:
            # Check if product exists by slug
            result = await db.execute(select(Product).where(Product.slug == slug))
            product = result.scalar_one_or_none()

            if not product:
                product = Product(
                    name=item.name[:500],
                    slug=slug,
                    category=query[:200],
                    image_url=item.image_url,
                )
                db.add(product)
                await db.flush()

            # Check if offer exists for this product + store + url
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
                    score=7.0,
                )
                db.add(offer)

            saved_products.append(product)
        except Exception as e:
            logger.error(f"Failed to save product '{item.name[:50]}': {e}")
            continue

    try:
        await db.commit()
        logger.info(f"Saved {len(saved_products)} products for query '{query}'")
    except Exception as e:
        logger.error(f"Failed to commit: {e}")
        await db.rollback()
        return []

    return saved_products

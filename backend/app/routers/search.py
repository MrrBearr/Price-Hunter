import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_

from app.database import get_db
from app.models.product import Product
from app.models.offer import Offer
from app.schemas.product import ProductResponse
from app.services.redis_service import RedisService
from app.services.search_service import search_and_save

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/", response_model=List[ProductResponse])
async def search_products(
    q: str = Query(..., min_length=2, description="Search query"),
    category: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    store: Optional[str] = None,
    sort_by: str = Query("relevance", enum=["relevance", "price_asc", "price_desc", "name"]),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    logger.info(f"Search request: q={q}, sort_by={sort_by}, page={page}")

    # Check cache first
    cache_key = f"search:{q}:{category}:{min_price}:{max_price}:{store}:{sort_by}:{page}"
    cached = await RedisService.cache_get(cache_key)
    if cached:
        return cached

    # Search in database
    products = await _query_products(db, q, category, sort_by, page, per_page)

    # If no results, fetch from external APIs and save
    if not products and page == 1:
        logger.info(f"No results in DB, fetching from external APIs for: {q}")
        await search_and_save(q, db)
        # Re-query after saving
        products = await _query_products(db, q, category, sort_by, page, per_page)
        logger.info(f"After external fetch, found {len(products)} products")

    # Build response with offer stats
    response = []
    for product in products:
        offers_query = select(
            func.count(Offer.id),
            func.min(Offer.price),
            func.max(Offer.price),
        ).where(Offer.product_id == product.id, Offer.is_available == True)

        if min_price:
            offers_query = offers_query.where(Offer.price >= min_price)
        if max_price:
            offers_query = offers_query.where(Offer.price <= max_price)

        offers_result = await db.execute(offers_query)
        stats = offers_result.one()

        if (min_price or max_price) and stats[0] == 0:
            continue

        response.append(ProductResponse(
            id=product.id,
            name=product.name,
            slug=product.slug,
            description=product.description,
            category=product.category,
            brand=product.brand,
            image_url=product.image_url,
            min_price=float(stats[1]) if stats[1] else None,
            max_price=float(stats[2]) if stats[2] else None,
            offers_count=stats[0],
            created_at=product.created_at,
        ))

    # Sort by price if needed
    if sort_by == "price_asc":
        response.sort(key=lambda x: x.min_price or float('inf'))
    elif sort_by == "price_desc":
        response.sort(key=lambda x: x.min_price or 0, reverse=True)

    # Cache for 5 minutes
    if response:
        await RedisService.cache_set(
            cache_key,
            [r.model_dump(mode="json") for r in response],
            expire=300,
        )

    return response


async def _query_products(
    db: AsyncSession,
    q: str,
    category: Optional[str],
    sort_by: str,
    page: int,
    per_page: int,
) -> List[Product]:
    """Query products from database."""
    query = select(Product).where(
        or_(
            Product.name.ilike(f"%{q}%"),
            Product.category.ilike(f"%{q}%"),
        )
    )

    if category:
        query = query.where(Product.category == category)

    if sort_by == "name":
        query = query.order_by(Product.name.asc())
    else:
        query = query.order_by(Product.created_at.desc())

    query = query.offset((page - 1) * per_page).limit(per_page)
    result = await db.execute(query)
    return list(result.scalars().all())


@router.post("/trigger")
async def trigger_search(
    q: str = Query(..., min_length=2),
    db: AsyncSession = Depends(get_db),
):
    """Trigger a search - does direct HTTP search and optionally queues to Redis."""
    # Queue to Redis if available (Docker mode)
    await RedisService.publish_task("scraping_queue", {
        "query": q,
        "stores": ["amazon", "mercadolivre", "shopee"],
    })

    # Direct search (Vercel/serverless mode)
    await search_and_save(q, db)

    return {"message": "Search triggered and completed", "query": q}

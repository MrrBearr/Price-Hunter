from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_

from app.database import get_db
from app.models.product import Product
from app.models.offer import Offer
from app.models.store import Store
from app.schemas.product import ProductResponse
from app.services.redis_service import RedisService
from app.services.search_service import search_and_save

router = APIRouter()


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
    # Check cache
    cache_key = f"search:{q}:{category}:{min_price}:{max_price}:{store}:{sort_by}:{page}"
    cached = await RedisService.cache_get(cache_key)
    if cached:
        return cached

    # Build query
    query = select(Product).where(
        or_(
            Product.name.ilike(f"%{q}%"),
            Product.brand.ilike(f"%{q}%"),
            Product.category.ilike(f"%{q}%"),
        )
    )

    if category:
        query = query.where(Product.category == category)

    # Sort
    if sort_by == "name":
        query = query.order_by(Product.name.asc())
    else:
        query = query.order_by(Product.created_at.desc())

    query = query.offset((page - 1) * per_page).limit(per_page)
    result = await db.execute(query)
    products = result.scalars().all()

    # If no results in DB, search external APIs and save
    if not products and page == 1:
        await search_and_save(q, db)
        await db.commit()
        # Re-query after saving
        re_query = select(Product).where(
            or_(
                Product.name.ilike(f"%{q}%"),
                Product.brand.ilike(f"%{q}%"),
                Product.category.ilike(f"%{q}%"),
            )
        )
        if sort_by == "name":
            re_query = re_query.order_by(Product.name.asc())
        else:
            re_query = re_query.order_by(Product.created_at.desc())
        re_query = re_query.limit(per_page)
        result = await db.execute(re_query)
        products = result.scalars().all()

    response = []
    for product in products:
        # Get offers data
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

        if min_price or max_price:
            if stats[0] == 0:
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

    # Cache results for 5 minutes
    await RedisService.cache_set(cache_key, [r.model_dump(mode="json") for r in response], expire=300)

    return response


@router.post("/trigger")
async def trigger_search(
    q: str = Query(..., min_length=2),
    db: AsyncSession = Depends(get_db),
):
    """Trigger a search - on serverless, does direct HTTP search. With Redis, queues scraping."""
    # Try to queue to Redis (Docker mode)
    await RedisService.publish_task("scraping_queue", {
        "query": q,
        "stores": ["amazon", "mercadolivre", "shopee"],
    })

    # Also do direct search (Vercel/serverless mode)
    await search_and_save(q, db)
    await db.commit()

    return {"message": "Search triggered", "query": q}

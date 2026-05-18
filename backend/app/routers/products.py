from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.database import get_db
from app.models.product import Product
from app.models.offer import Offer
from app.models.price_history import PriceHistory
from app.schemas.product import ProductResponse
from app.schemas.price_history import PriceHistoryResponse

router = APIRouter()


@router.get("/", response_model=List[ProductResponse])
async def get_products(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    category: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    query = select(Product)
    if category:
        query = query.where(Product.category == category)
    query = query.offset((page - 1) * per_page).limit(per_page)

    result = await db.execute(query)
    products = result.scalars().all()

    response = []
    for product in products:
        # Get offer stats
        offers_result = await db.execute(
            select(
                func.count(Offer.id),
                func.min(Offer.price),
                func.max(Offer.price),
            ).where(Offer.product_id == product.id, Offer.is_available == True)
        )
        stats = offers_result.one()

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

    return response


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(product_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    offers_result = await db.execute(
        select(
            func.count(Offer.id),
            func.min(Offer.price),
            func.max(Offer.price),
        ).where(Offer.product_id == product.id, Offer.is_available == True)
    )
    stats = offers_result.one()

    return ProductResponse(
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
    )


@router.get("/{product_id}/history", response_model=List[PriceHistoryResponse])
async def get_price_history(
    product_id: UUID,
    days: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
):
    from datetime import datetime, timedelta

    start_date = datetime.utcnow() - timedelta(days=days)

    result = await db.execute(
        select(PriceHistory)
        .where(
            PriceHistory.product_id == product_id,
            PriceHistory.recorded_at >= start_date,
        )
        .order_by(PriceHistory.recorded_at.asc())
    )
    history = result.scalars().all()

    return [
        PriceHistoryResponse(
            id=h.id,
            offer_id=h.offer_id,
            product_id=h.product_id,
            store_id=h.store_id,
            price=float(h.price),
            shipping_cost=float(h.shipping_cost),
            recorded_at=h.recorded_at,
        )
        for h in history
    ]

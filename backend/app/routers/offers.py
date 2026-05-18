from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.offer import Offer
from app.models.store import Store
from app.schemas.offer import OfferResponse

router = APIRouter()


@router.get("/product/{product_id}", response_model=List[OfferResponse])
async def get_offers_by_product(
    product_id: UUID,
    sort_by: str = Query("score", enum=["price", "score", "shipping"]),
    db: AsyncSession = Depends(get_db),
):
    query = select(Offer, Store).join(Store, Offer.store_id == Store.id).where(
        Offer.product_id == product_id,
        Offer.is_available == True,
    )

    if sort_by == "price":
        query = query.order_by(Offer.price.asc())
    elif sort_by == "shipping":
        query = query.order_by(Offer.shipping_cost.asc())
    else:
        query = query.order_by(Offer.score.desc())

    result = await db.execute(query)
    rows = result.all()

    return [
        OfferResponse(
            id=offer.id,
            product_id=offer.product_id,
            store_id=offer.store_id,
            price=float(offer.price),
            original_price=float(offer.original_price) if offer.original_price else None,
            shipping_cost=float(offer.shipping_cost),
            shipping_time=offer.shipping_time,
            url=offer.url,
            seller_name=offer.seller_name,
            seller_rating=float(offer.seller_rating) if offer.seller_rating else None,
            is_available=offer.is_available,
            score=float(offer.score),
            store_name=store.name,
            store_slug=store.slug,
            last_checked=offer.last_checked,
            created_at=offer.created_at,
        )
        for offer, store in rows
    ]


@router.get("/{offer_id}", response_model=OfferResponse)
async def get_offer(offer_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Offer, Store).join(Store, Offer.store_id == Store.id).where(Offer.id == offer_id)
    )
    row = result.one_or_none()
    if not row:
        raise HTTPException(status_code=404, detail="Offer not found")

    offer, store = row
    return OfferResponse(
        id=offer.id,
        product_id=offer.product_id,
        store_id=offer.store_id,
        price=float(offer.price),
        original_price=float(offer.original_price) if offer.original_price else None,
        shipping_cost=float(offer.shipping_cost),
        shipping_time=offer.shipping_time,
        url=offer.url,
        seller_name=offer.seller_name,
        seller_rating=float(offer.seller_rating) if offer.seller_rating else None,
        is_available=offer.is_available,
        score=float(offer.score),
        store_name=store.name,
        store_slug=store.slug,
        last_checked=offer.last_checked,
        created_at=offer.created_at,
    )

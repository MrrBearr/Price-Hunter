from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.database import get_db
from app.models.favorite import Favorite
from app.models.product import Product
from app.models.offer import Offer
from app.models.user import User
from app.schemas.favorite import FavoriteCreate, FavoriteResponse
from app.auth import get_current_user

router = APIRouter()


@router.get("/", response_model=List[FavoriteResponse])
async def get_favorites(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Favorite, Product)
        .join(Product, Favorite.product_id == Product.id)
        .where(Favorite.user_id == current_user.id)
        .order_by(Favorite.created_at.desc())
    )
    rows = result.all()

    response = []
    for fav, product in rows:
        price_result = await db.execute(
            select(func.min(Offer.price))
            .where(Offer.product_id == product.id, Offer.is_available == True)
        )
        min_price = price_result.scalar()

        response.append(FavoriteResponse(
            id=fav.id,
            user_id=fav.user_id,
            product_id=fav.product_id,
            product_name=product.name,
            product_image=product.image_url,
            min_price=float(min_price) if min_price else None,
            created_at=fav.created_at,
        ))

    return response


@router.post("/", response_model=FavoriteResponse, status_code=201)
async def add_favorite(
    fav_data: FavoriteCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Check if already favorited
    result = await db.execute(
        select(Favorite).where(
            Favorite.user_id == current_user.id,
            Favorite.product_id == fav_data.product_id,
        )
    )
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Product already in favorites")

    # Verify product exists
    result = await db.execute(select(Product).where(Product.id == fav_data.product_id))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    favorite = Favorite(user_id=current_user.id, product_id=fav_data.product_id)
    db.add(favorite)
    await db.flush()
    await db.refresh(favorite)

    return FavoriteResponse(
        id=favorite.id,
        user_id=favorite.user_id,
        product_id=favorite.product_id,
        product_name=product.name,
        product_image=product.image_url,
        min_price=None,
        created_at=favorite.created_at,
    )


@router.delete("/{product_id}")
async def remove_favorite(
    product_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Favorite).where(
            Favorite.user_id == current_user.id,
            Favorite.product_id == product_id,
        )
    )
    favorite = result.scalar_one_or_none()
    if not favorite:
        raise HTTPException(status_code=404, detail="Favorite not found")

    await db.delete(favorite)
    return {"message": "Removed from favorites"}

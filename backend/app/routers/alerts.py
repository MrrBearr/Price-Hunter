from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.database import get_db
from app.models.alert import Alert
from app.models.product import Product
from app.models.offer import Offer
from app.models.user import User
from app.schemas.alert import AlertCreate, AlertResponse
from app.auth import get_current_user

router = APIRouter()


@router.get("/", response_model=List[AlertResponse])
async def get_alerts(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Alert, Product)
        .join(Product, Alert.product_id == Product.id)
        .where(Alert.user_id == current_user.id)
        .order_by(Alert.created_at.desc())
    )
    rows = result.all()

    response = []
    for alert, product in rows:
        # Get current min price
        price_result = await db.execute(
            select(func.min(Offer.price))
            .where(Offer.product_id == product.id, Offer.is_available == True)
        )
        current_price = price_result.scalar()

        response.append(AlertResponse(
            id=alert.id,
            user_id=alert.user_id,
            product_id=alert.product_id,
            target_price=float(alert.target_price),
            is_active=alert.is_active,
            triggered=alert.triggered,
            triggered_at=alert.triggered_at,
            product_name=product.name,
            current_price=float(current_price) if current_price else None,
            created_at=alert.created_at,
        ))

    return response


@router.post("/", response_model=AlertResponse, status_code=201)
async def create_alert(
    alert_data: AlertCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Verify product exists
    result = await db.execute(select(Product).where(Product.id == alert_data.product_id))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    alert = Alert(
        user_id=current_user.id,
        product_id=alert_data.product_id,
        target_price=alert_data.target_price,
    )
    db.add(alert)
    await db.flush()
    await db.refresh(alert)

    return AlertResponse(
        id=alert.id,
        user_id=alert.user_id,
        product_id=alert.product_id,
        target_price=float(alert.target_price),
        is_active=alert.is_active,
        triggered=alert.triggered,
        triggered_at=alert.triggered_at,
        product_name=product.name,
        current_price=None,
        created_at=alert.created_at,
    )


@router.delete("/{alert_id}")
async def delete_alert(
    alert_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Alert).where(Alert.id == alert_id, Alert.user_id == current_user.id)
    )
    alert = result.scalar_one_or_none()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    await db.delete(alert)
    return {"message": "Alert deleted"}

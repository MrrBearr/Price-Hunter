from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.coupon import Coupon, CouponTest
from app.models.store import Store
from app.schemas.coupon import CouponCreate, CouponResponse, CouponTestResponse
from app.auth import get_current_user
from app.models.user import User
from app.services.redis_service import RedisService

router = APIRouter()


@router.get("/", response_model=List[CouponResponse])
async def get_coupons(
    store_id: Optional[UUID] = None,
    active_only: bool = True,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    query = select(Coupon, Store).join(Store, Coupon.store_id == Store.id)

    if store_id:
        query = query.where(Coupon.store_id == store_id)
    if active_only:
        query = query.where(Coupon.is_active == True)

    query = query.order_by(Coupon.success_rate.desc())
    query = query.offset((page - 1) * per_page).limit(per_page)

    result = await db.execute(query)
    rows = result.all()

    return [
        CouponResponse(
            id=coupon.id,
            store_id=coupon.store_id,
            code=coupon.code,
            description=coupon.description,
            discount_type=coupon.discount_type,
            discount_value=float(coupon.discount_value),
            minimum_purchase=float(coupon.minimum_purchase),
            success_rate=float(coupon.success_rate),
            is_active=coupon.is_active,
            expires_at=coupon.expires_at,
            store_name=store.name,
            created_at=coupon.created_at,
        )
        for coupon, store in rows
    ]


@router.post("/", response_model=CouponResponse, status_code=201)
async def create_coupon(
    coupon_data: CouponCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    coupon = Coupon(
        store_id=coupon_data.store_id,
        code=coupon_data.code,
        description=coupon_data.description,
        discount_type=coupon_data.discount_type,
        discount_value=coupon_data.discount_value,
        minimum_purchase=coupon_data.minimum_purchase,
        expires_at=coupon_data.expires_at,
    )
    db.add(coupon)
    await db.flush()
    await db.refresh(coupon)

    result = await db.execute(select(Store).where(Store.id == coupon.store_id))
    store = result.scalar_one_or_none()

    return CouponResponse(
        id=coupon.id,
        store_id=coupon.store_id,
        code=coupon.code,
        description=coupon.description,
        discount_type=coupon.discount_type,
        discount_value=float(coupon.discount_value),
        minimum_purchase=float(coupon.minimum_purchase),
        success_rate=float(coupon.success_rate),
        is_active=coupon.is_active,
        expires_at=coupon.expires_at,
        store_name=store.name if store else None,
        created_at=coupon.created_at,
    )


@router.post("/{coupon_id}/test", response_model=dict)
async def test_coupon(
    coupon_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Coupon).where(Coupon.id == coupon_id))
    coupon = result.scalar_one_or_none()
    if not coupon:
        raise HTTPException(status_code=404, detail="Coupon not found")

    # Queue coupon test
    await RedisService.publish_task("coupon_test_queue", {
        "coupon_id": str(coupon_id),
        "code": coupon.code,
        "store_id": str(coupon.store_id),
    })

    return {"message": "Coupon test queued", "coupon_id": str(coupon_id)}


@router.get("/{coupon_id}/tests", response_model=List[CouponTestResponse])
async def get_coupon_tests(coupon_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(CouponTest)
        .where(CouponTest.coupon_id == coupon_id)
        .order_by(CouponTest.tested_at.desc())
        .limit(20)
    )
    tests = result.scalars().all()
    return tests

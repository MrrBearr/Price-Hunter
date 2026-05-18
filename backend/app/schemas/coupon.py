from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime


class CouponCreate(BaseModel):
    store_id: UUID
    code: str
    description: Optional[str] = None
    discount_type: str  # percentage, fixed, shipping
    discount_value: float
    minimum_purchase: float = 0.0
    expires_at: Optional[datetime] = None


class CouponResponse(BaseModel):
    id: UUID
    store_id: UUID
    code: str
    description: Optional[str] = None
    discount_type: str
    discount_value: float
    minimum_purchase: float
    success_rate: float
    is_active: bool
    expires_at: Optional[datetime] = None
    store_name: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class CouponTestResponse(BaseModel):
    id: UUID
    coupon_id: UUID
    tested_at: datetime
    success: bool
    discount_applied: Optional[float] = None
    error_message: Optional[str] = None

    class Config:
        from_attributes = True

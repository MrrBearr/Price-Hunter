from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime


class OfferCreate(BaseModel):
    product_id: UUID
    store_id: UUID
    price: float
    original_price: Optional[float] = None
    shipping_cost: float = 0.0
    shipping_time: Optional[str] = None
    url: str
    seller_name: Optional[str] = None
    seller_rating: Optional[float] = None


class OfferResponse(BaseModel):
    id: UUID
    product_id: UUID
    store_id: UUID
    price: float
    original_price: Optional[float] = None
    shipping_cost: float
    shipping_time: Optional[str] = None
    url: str
    seller_name: Optional[str] = None
    seller_rating: Optional[float] = None
    is_available: bool
    score: float
    store_name: Optional[str] = None
    store_slug: Optional[str] = None
    last_checked: datetime
    created_at: datetime

    class Config:
        from_attributes = True

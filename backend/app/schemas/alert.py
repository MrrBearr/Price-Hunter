from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime


class AlertCreate(BaseModel):
    product_id: UUID
    target_price: float


class AlertResponse(BaseModel):
    id: UUID
    user_id: UUID
    product_id: UUID
    target_price: float
    is_active: bool
    triggered: bool
    triggered_at: Optional[datetime] = None
    product_name: Optional[str] = None
    current_price: Optional[float] = None
    created_at: datetime

    class Config:
        from_attributes = True

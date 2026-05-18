from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional


class PriceHistoryResponse(BaseModel):
    id: UUID
    offer_id: UUID
    product_id: UUID
    store_id: UUID
    price: float
    shipping_cost: float
    store_name: Optional[str] = None
    recorded_at: datetime

    class Config:
        from_attributes = True

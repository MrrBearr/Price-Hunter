from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional


class FavoriteCreate(BaseModel):
    product_id: UUID


class FavoriteResponse(BaseModel):
    id: UUID
    user_id: UUID
    product_id: UUID
    product_name: Optional[str] = None
    product_image: Optional[str] = None
    min_price: Optional[float] = None
    created_at: datetime

    class Config:
        from_attributes = True

from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from datetime import datetime


class ProductCreate(BaseModel):
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    brand: Optional[str] = None
    image_url: Optional[str] = None
    ean: Optional[str] = None


class ProductSearch(BaseModel):
    query: str
    category: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    stores: Optional[List[str]] = None
    sort_by: Optional[str] = "score"  # price, score, name
    page: int = 1
    per_page: int = 20


class ProductResponse(BaseModel):
    id: UUID
    name: str
    slug: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    brand: Optional[str] = None
    image_url: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    offers_count: Optional[int] = 0
    created_at: datetime

    class Config:
        from_attributes = True

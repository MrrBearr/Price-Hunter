import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, Numeric, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base


class Offer(Base):
    __tablename__ = "offers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    store_id = Column(UUID(as_uuid=True), ForeignKey("stores.id", ondelete="CASCADE"), nullable=False)
    price = Column(Numeric(12, 2), nullable=False)
    original_price = Column(Numeric(12, 2))
    shipping_cost = Column(Numeric(10, 2), default=0.00)
    shipping_time = Column(String(100))
    url = Column(String(1000), nullable=False)
    seller_name = Column(String(255))
    seller_rating = Column(Numeric(3, 2))
    is_available = Column(Boolean, default=True)
    score = Column(Numeric(5, 2), default=0.00)
    last_checked = Column(DateTime(timezone=True), default=datetime.utcnow)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    product = relationship("Product", back_populates="offers")
    store = relationship("Store", back_populates="offers")
    price_history = relationship("PriceHistory", back_populates="offer", cascade="all, delete-orphan")

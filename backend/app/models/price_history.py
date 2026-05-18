import uuid
from datetime import datetime
from sqlalchemy import Column, DateTime, Numeric, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base


class PriceHistory(Base):
    __tablename__ = "price_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    offer_id = Column(UUID(as_uuid=True), ForeignKey("offers.id", ondelete="CASCADE"), nullable=False)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    store_id = Column(UUID(as_uuid=True), ForeignKey("stores.id", ondelete="CASCADE"), nullable=False)
    price = Column(Numeric(12, 2), nullable=False)
    shipping_cost = Column(Numeric(10, 2), default=0.00)
    recorded_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    offer = relationship("Offer", back_populates="price_history")
    product = relationship("Product", back_populates="price_history")
    store = relationship("Store", back_populates="price_history")

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base


class Store(Base):
    __tablename__ = "stores"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    url = Column(String(500), nullable=False)
    logo_url = Column(String(500))
    is_active = Column(Boolean, default=True)
    reputation_score = Column(Numeric(3, 2), default=0.00)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    offers = relationship("Offer", back_populates="store", cascade="all, delete-orphan")
    coupons = relationship("Coupon", back_populates="store", cascade="all, delete-orphan")
    price_history = relationship("PriceHistory", back_populates="store", cascade="all, delete-orphan")

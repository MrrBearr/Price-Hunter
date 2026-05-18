import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, Numeric, Integer, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base


class Coupon(Base):
    __tablename__ = "coupons"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    store_id = Column(UUID(as_uuid=True), ForeignKey("stores.id", ondelete="CASCADE"), nullable=False)
    code = Column(String(100), nullable=False, index=True)
    description = Column(Text)
    discount_type = Column(String(20), nullable=False)  # percentage, fixed, shipping
    discount_value = Column(Numeric(10, 2), nullable=False)
    minimum_purchase = Column(Numeric(10, 2), default=0.00)
    max_uses = Column(Integer)
    current_uses = Column(Integer, default=0)
    success_rate = Column(Numeric(5, 2), default=0.00)
    is_active = Column(Boolean, default=True)
    expires_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    store = relationship("Store", back_populates="coupons")
    tests = relationship("CouponTest", back_populates="coupon", cascade="all, delete-orphan")


class CouponTest(Base):
    __tablename__ = "coupon_tests"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    coupon_id = Column(UUID(as_uuid=True), ForeignKey("coupons.id", ondelete="CASCADE"), nullable=False)
    tested_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    success = Column(Boolean, nullable=False)
    discount_applied = Column(Numeric(10, 2))
    error_message = Column(Text)
    test_url = Column(String(1000))

    coupon = relationship("Coupon", back_populates="tests")

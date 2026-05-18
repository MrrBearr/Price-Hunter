import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.database import Base


class Log(Base):
    __tablename__ = "logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    level = Column(String(20), nullable=False, default="info")
    source = Column(String(100), nullable=False)
    message = Column(Text, nullable=False)
    metadata = Column(JSONB)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

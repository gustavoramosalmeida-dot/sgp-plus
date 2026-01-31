"""Session model"""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import Column, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import relationship

from sgp_plus.db.base import Base


class Session(Base):
    """Session model"""

    __tablename__ = "sessions"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=False, index=True)
    revoked_at = Column(DateTime, nullable=True)
    user_agent = Column(String(512), nullable=True)
    ip = Column(String(45), nullable=True)

    # Relationships
    user = relationship("User", back_populates="sessions")

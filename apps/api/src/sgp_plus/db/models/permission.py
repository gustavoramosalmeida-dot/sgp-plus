"""Permission model"""

from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

from sgp_plus.db.base import Base


class Permission(Base):
    """Permission model"""

    __tablename__ = "permissions"

    id = Column(String(50), primary_key=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)

    # Relationships
    roles = relationship("Role", secondary="role_permissions", back_populates="permissions")

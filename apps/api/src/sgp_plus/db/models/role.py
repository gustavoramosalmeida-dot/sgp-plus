"""Role model"""

from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

from sgp_plus.db.base import Base


class Role(Base):
    """Role model"""

    __tablename__ = "roles"

    id = Column(String(50), primary_key=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)

    # Relationships
    users = relationship("User", secondary="user_roles", back_populates="roles")
    permissions = relationship("Permission", secondary="role_permissions", back_populates="roles")

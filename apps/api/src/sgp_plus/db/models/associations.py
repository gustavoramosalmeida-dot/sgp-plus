"""Association tables for many-to-many relationships"""

from sqlalchemy import Column, ForeignKey, String, Table
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from sgp_plus.db.base import Base

# User-Role association
user_roles = Table(
    "user_roles",
    Base.metadata,
    Column("user_id", PGUUID(as_uuid=True), ForeignKey("users.id"), primary_key=True),
    Column("role_id", String(50), ForeignKey("roles.id"), primary_key=True),
)

# Role-Permission association
role_permissions = Table(
    "role_permissions",
    Base.metadata,
    Column("role_id", String(50), ForeignKey("roles.id"), primary_key=True),
    Column("permission_id", String(50), ForeignKey("permissions.id"), primary_key=True),
)

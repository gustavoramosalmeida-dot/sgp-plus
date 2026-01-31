"""Auth schemas"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, field_validator, ConfigDict


class LoginRequest(BaseModel):
    """Login request"""

    email: str
    password: str

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        """Validate email format minimally (accepts internal domains like .local)"""
        if not isinstance(v, str):
            raise ValueError("email must be a string")
        
        email = v.strip().lower()
        
        # Basic validation: must contain exactly one @
        if email.count("@") != 1:
            raise ValueError("email must contain exactly one @")
        
        parts = email.split("@")
        local_part = parts[0]
        domain_part = parts[1]
        
        # Both parts must be non-empty
        if not local_part:
            raise ValueError("email local part cannot be empty")
        if not domain_part:
            raise ValueError("email domain part cannot be empty")
        
        return email


class UserResponse(BaseModel):
    """User response"""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: str
    is_active: bool
    created_at: datetime


class RoleResponse(BaseModel):
    """Role response"""

    model_config = ConfigDict(from_attributes=True)

    id: str
    code: str
    name: str


class PermissionResponse(BaseModel):
    """Permission response"""

    model_config = ConfigDict(from_attributes=True)

    id: str
    code: str
    name: str


class LoginResponse(BaseModel):
    """Login response"""

    user: UserResponse
    roles: list[RoleResponse]
    permissions: list[PermissionResponse]


class MeResponse(BaseModel):
    """Me response (same as LoginResponse)"""

    user: UserResponse
    roles: list[RoleResponse]
    permissions: list[PermissionResponse]

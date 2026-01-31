"""RBAC (Role-Based Access Control)"""

from typing import Annotated

from fastapi import Depends, HTTPException, status

from sgp_plus.db.session import get_db
from sgp_plus.core.security import get_current_user
from sgp_plus.db.models.user import User

from sqlalchemy.orm import Session


def require_permissions(*permission_codes: str):
    """
    Dependency to require specific permissions.
    Usage: @app.get("/route", dependencies=[Depends(require_permissions("users.read"))])
    """

    async def permission_checker(
        db: Annotated[Session, Depends(get_db)],
        current_user: Annotated[User, Depends(get_current_user)],
    ) -> User:
        """Check if user has required permissions"""
        if not current_user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is inactive",
            )

        # Get user permissions
        user_permissions = set()
        for role in current_user.roles:
            for perm in role.permissions:
                user_permissions.add(perm.code)

        # Check if user has all required permissions
        required = set(permission_codes)
        missing = required - user_permissions

        if missing:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing permissions: {', '.join(missing)}",
            )

        return current_user

    return permission_checker

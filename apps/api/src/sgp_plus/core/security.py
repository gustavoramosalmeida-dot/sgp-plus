"""Security utilities"""
from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, Request, Response, status
from passlib.context import CryptContext
from sqlalchemy.orm import Session, selectinload

from sgp_plus.core.config import settings
from sgp_plus.db.session import get_db
from sgp_plus.db.models.user import User
from sgp_plus.db.models.role import Role

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a password"""
    password_bytes = len(password.encode("utf-8"))
    if password_bytes > 72:
        raise ValueError(
            "Password too long for bcrypt (max 72 bytes). "
            "Use a shorter password or adjust policy."
        )
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash"""
    return pwd_context.verify(plain_password, hashed_password)


def set_session_cookie(response: Response, session_id: UUID) -> None:
    """Set HttpOnly session cookie"""
    max_age = settings.session_ttl_minutes * 60
    response.set_cookie(
        key=settings.cookie_name,
        value=str(session_id),
        max_age=max_age,
        httponly=True,
        secure=settings.cookie_secure,
        samesite=settings.cookie_samesite,
        domain=settings.cookie_domain,
        path=settings.cookie_path,
    )


def clear_session_cookie(response: Response) -> None:
    """Clear session cookie (same path/domain as set)"""
    response.delete_cookie(
        key=settings.cookie_name,
        path=settings.cookie_path,
        domain=settings.cookie_domain,
        httponly=True,
        secure=settings.cookie_secure,
        samesite=settings.cookie_samesite,
    )
def get_current_user(
    request: Request,
    db: Annotated[Session, Depends(get_db)],
) -> User:
    """Get current user from session cookie"""
    session_id = request.cookies.get(settings.cookie_name)

    if not session_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    try:
        session_uuid = UUID(session_id)
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    from sgp_plus.features.auth.repository import AuthRepository

    repository = AuthRepository()
    session = repository.get_valid_session(db, session_uuid)

    if not session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired or invalid",
        )

    user = (
        db.query(User)
        .filter(User.id == session.user_id)
        .options(
            selectinload(User.roles).selectinload(Role.permissions),
        )
        .first()
    )

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )

    return user

"""Auth router"""

import logging
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Request, Response, status

logger = logging.getLogger(__name__)
from sqlalchemy.orm import Session

from sgp_plus.db.session import get_db
from sgp_plus.core.security import (
    get_current_user,
    set_session_cookie,
    clear_session_cookie,
)
from sgp_plus.features.auth.schemas import (
    LoginRequest,
    LoginResponse,
    MeResponse,
    UserResponse,
    RoleResponse,
    PermissionResponse,
)
from sgp_plus.features.auth.service import AuthService
from sgp_plus.features.auth.repository import AuthRepository
from sgp_plus.db.models.user import User
from sgp_plus.shared.utils import get_client_ip, get_user_agent
from sgp_plus.core.config import settings

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse, status_code=status.HTTP_200_OK)
async def login(
    request: Request,
    response: Response,
    login_data: LoginRequest,
    db: Annotated[Session, Depends(get_db)],
):
    """Login endpoint"""
    service = AuthService(db)
    user = service.authenticate(login_data.email, login_data.password)

    # Create session
    repository = AuthRepository()
    session = repository.create_session(
        db,
        user.id,
        user_agent=get_user_agent(request),
        ip=get_client_ip(request),
    )

    # Set cookie
    set_session_cookie(response, session.id)

    # Get user data
    roles = service.get_user_roles(user)
    permissions = service.get_user_permissions(user)

    return LoginResponse(
        user=UserResponse.model_validate(user),
        roles=[RoleResponse(**r) for r in roles],
        permissions=[PermissionResponse(**p) for p in permissions],
    )


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(
    request: Request,
    response: Response,
    db: Annotated[Session, Depends(get_db)],
):
    """Logout endpoint"""
    session_id = request.cookies.get(settings.cookie_name)
    if session_id:
        try:
            repository = AuthRepository()
            repository.revoke_session(db, UUID(session_id))
        except ValueError:
            pass  # Invalid UUID, ignora
        except Exception:
            logger.exception("logout: falha ao revogar sessão no DB")

    clear_session_cookie(response)
    return {"message": "Logged out"}


@router.get("/me", response_model=MeResponse)
async def me(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    """Get current user info"""
    service = AuthService(db)
    roles = service.get_user_roles(current_user)
    permissions = service.get_user_permissions(current_user)

    return MeResponse(
        user=UserResponse.model_validate(current_user),
        roles=[RoleResponse(**r) for r in roles],
        permissions=[PermissionResponse(**p) for p in permissions],
    )

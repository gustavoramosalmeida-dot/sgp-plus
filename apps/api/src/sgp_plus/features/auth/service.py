"""Auth service"""

from uuid import UUID

from sqlalchemy.orm import Session

from sgp_plus.db.models.user import User
from sgp_plus.core.security import verify_password
from sgp_plus.features.auth.repository import AuthRepository
from sgp_plus.shared.errors import AuthenticationError


class AuthService:
    """Auth service"""

    def __init__(self, db: Session):
        self.db = db
        self.repository = AuthRepository()

    def authenticate(self, email: str, password: str) -> User:
        """Authenticate user"""
        user = self.repository.get_user_by_email(self.db, email)

        if not user:
            raise AuthenticationError()

        if not user.is_active:
            raise AuthenticationError("User is inactive")

        if not verify_password(password, user.password_hash):
            raise AuthenticationError()

        return user

    def get_user_permissions(self, user: User) -> list[dict]:
        """Get user permissions"""
        permissions = []
        seen = set()
        for role in user.roles:
            for perm in role.permissions:
                if perm.code not in seen:
                    permissions.append({"id": perm.id, "code": perm.code, "name": perm.name})
                    seen.add(perm.code)
        return permissions

    def get_user_roles(self, user: User) -> list[dict]:
        """Get user roles"""
        return [{"id": role.id, "code": role.code, "name": role.name} for role in user.roles]

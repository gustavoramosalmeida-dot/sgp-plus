"""Auth repository"""

from datetime import datetime
from uuid import UUID

from sqlalchemy.orm import Session
from sqlalchemy import and_

from sgp_plus.db.models.user import User
from sgp_plus.db.models.session import Session as SessionModel
from sgp_plus.core.session_utils import get_session_expires_at


class AuthRepository:
    """Auth repository"""

    @staticmethod
    def get_user_by_email(db: Session, email: str) -> User | None:
        """Get user by email"""
        return db.query(User).filter(User.email == email).first()

    @staticmethod
    def create_session(
        db: Session,
        user_id: UUID,
        user_agent: str | None = None,
        ip: str | None = None,
    ) -> SessionModel:
        """Create a new session"""
        session = SessionModel(
            user_id=user_id,
            expires_at=get_session_expires_at(),
            user_agent=user_agent,
            ip=ip,
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        return session

    @staticmethod
    def get_valid_session(db: Session, session_id: UUID) -> SessionModel | None:
        """Get valid session by ID"""
        now = datetime.utcnow()
        return (
            db.query(SessionModel)
            .filter(
                and_(
                    SessionModel.id == session_id,
                    SessionModel.expires_at > now,
                    SessionModel.revoked_at.is_(None),
                )
            )
            .first()
        )

    @staticmethod
    def revoke_session(db: Session, session_id: UUID) -> None:
        """Revoke a session"""
        session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
        if session:
            session.revoked_at = datetime.utcnow()
            db.commit()

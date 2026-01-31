"""Session-related utilities."""

from datetime import datetime, timedelta

from sgp_plus.core.config import settings


def get_session_expires_at() -> datetime:
    """Get session expiration datetime."""
    return datetime.utcnow() + timedelta(minutes=settings.session_ttl_minutes)


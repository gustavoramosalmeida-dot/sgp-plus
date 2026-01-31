"""Config validation tests"""

import pytest

from pydantic import ValidationError


def test_cors_origins_wildcard_rejected():
    """CORS_ORIGINS com '*' deve falhar no startup (allow_credentials + cookie auth)."""
    from sgp_plus.core.config import Settings

    with pytest.raises((ValueError, ValidationError)) as exc_info:
        Settings(cors_origins="*")

    msg = str(exc_info.value).lower()
    assert "cors_origins" in msg or "*" in str(exc_info.value)
    assert "allow_credentials" in msg or "cookie" in msg or "cannot" in msg

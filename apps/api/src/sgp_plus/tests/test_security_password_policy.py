"""Tests for password policy validation"""

import pytest

from sgp_plus.core.security import hash_password


def test_hash_password_rejects_password_over_72_bytes():
    """Test that hash_password raises ValueError for passwords >72 bytes"""
    # ASCII string: 73 chars = 73 bytes
    long_password = "A" * 73
    with pytest.raises(ValueError, match="Password too long for bcrypt"):
        hash_password(long_password)


def test_hash_password_accepts_password_exactly_72_bytes():
    """Test that hash_password accepts passwords exactly 72 bytes"""
    # ASCII string: 72 chars = 72 bytes
    password_72_bytes = "A" * 72
    # Should not raise
    result = hash_password(password_72_bytes)
    assert result is not None
    assert isinstance(result, str)
    assert result.startswith("$2b$")  # bcrypt hash format


def test_hash_password_accepts_password_under_72_bytes():
    """Test that hash_password accepts passwords <72 bytes"""
    password_short = "MySecurePassword123!"
    result = hash_password(password_short)
    assert result is not None
    assert isinstance(result, str)
    assert result.startswith("$2b$")


def test_hash_password_rejects_unicode_password_over_72_bytes():
    """Test that hash_password counts UTF-8 bytes, not characters"""
    # 25 emojis = 25 * 4 bytes = 100 bytes (over limit)
    unicode_password = "🔒" * 25
    with pytest.raises(ValueError, match="Password too long for bcrypt"):
        hash_password(unicode_password)

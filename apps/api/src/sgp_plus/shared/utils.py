"""Shared utilities"""

from typing import Any


def get_client_ip(request: Any) -> str:
    """Extract client IP from request"""
    if hasattr(request, "client") and request.client:
        return request.client.host
    return "unknown"


def get_user_agent(request: Any) -> str:
    """Extract user agent from request"""
    return request.headers.get("user-agent", "unknown")

"""Auth endpoint tests"""

import pytest
from fastapi.testclient import TestClient

from sgp_plus.db.models.user import User


def test_login_invalid_credentials(client: TestClient):
    """Test login with invalid credentials"""
    response = client.post(
        "/auth/login",
        json={"email": "invalid@example.com", "password": "wrong"},
    )
    assert response.status_code == 401


def test_login_valid_credentials(client: TestClient, test_user: User):
    """Test login with valid credentials"""
    response = client.post(
        "/auth/login",
        json={"email": "test@example.com", "password": "password123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "user" in data
    assert data["user"]["email"] == "test@example.com"
    assert "roles" in data
    assert "permissions" in data

    # Check cookie is set
    cookies = response.cookies
    assert "sgp_plus_session" in cookies


def test_me_authenticated(client: TestClient, test_user: User):
    """Test /auth/me when authenticated"""
    # Login first
    login_response = client.post(
        "/auth/login",
        json={"email": "test@example.com", "password": "password123"},
    )
    assert login_response.status_code == 200

    # Get me
    response = client.get("/auth/me")
    assert response.status_code == 200
    data = response.json()
    assert data["user"]["email"] == "test@example.com"


def test_me_unauthenticated(client: TestClient):
    """Test /auth/me when not authenticated"""
    response = client.get("/auth/me")
    assert response.status_code == 401


def test_me_invalid_cookie_not_500(client: TestClient):
    """Cookie com valor inválido (não-UUID) deve retornar 401, nunca 500"""
    response = client.get("/auth/me", cookies={"sgp_plus_session": "not-a-uuid"})
    assert response.status_code == 401
    assert response.json().get("detail") == "Not authenticated"


def test_logout(client: TestClient, test_user: User):
    """Test logout"""
    # Login first
    login_response = client.post(
        "/auth/login",
        json={"email": "test@example.com", "password": "password123"},
    )
    assert login_response.status_code == 200

    # Logout
    response = client.post("/auth/logout")
    assert response.status_code == 200

    # Try to access /auth/me after logout
    me_response = client.get("/auth/me")
    assert me_response.status_code == 401

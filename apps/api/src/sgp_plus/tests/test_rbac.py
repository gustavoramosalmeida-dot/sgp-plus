"""RBAC endpoint tests — prova server-side com /admin/ping"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from sgp_plus.db.models.user import User
from sgp_plus.db.models.role import Role
from sgp_plus.db.models.permission import Permission
from sgp_plus.core.security import hash_password


@pytest.fixture
def admin_user(db: Session):
    """Usuário com permissão rbac.manage (admin)."""
    perm = Permission(id="rbac.manage", code="rbac.manage", name="Manage RBAC")
    db.add(perm)
    db.flush()

    role = Role(id="admin", code="admin", name="Administrator")
    role.permissions = [perm]
    db.add(role)
    db.flush()

    user = User(
        email="admin@test.local",
        password_hash=hash_password("safe-pass"),
        is_active=True,
    )
    user.roles = [role]
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def test_admin_ping_without_permission(client: TestClient, test_user: User):
    """Usuário sem rbac.manage → GET /admin/ping retorna 403."""
    # test_user tem só test.read (conftest/test_auth)
    login = client.post(
        "/auth/login",
        json={"email": "test@example.com", "password": "password123"},
    )
    assert login.status_code == 200

    resp = client.get("/admin/ping")
    assert resp.status_code == 403
    assert "Missing permissions" in resp.json().get("detail", "")


def test_admin_ping_with_permission(client: TestClient, admin_user: User):
    """Admin com rbac.manage → GET /admin/ping retorna 200."""
    login = client.post(
        "/auth/login",
        json={"email": "admin@test.local", "password": "safe-pass"},
    )
    assert login.status_code == 200

    resp = client.get("/admin/ping")
    assert resp.status_code == 200
    assert resp.json() == {"ok": True}


def test_admin_ping_unauthenticated(client: TestClient):
    """Sem cookie → GET /admin/ping retorna 401."""
    resp = client.get("/admin/ping")
    assert resp.status_code == 401

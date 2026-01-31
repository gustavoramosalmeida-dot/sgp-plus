"""Pytest configuration"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from sgp_plus.db.base import Base
from sgp_plus.db.session import get_db
from sgp_plus.db.models.user import User
from sgp_plus.db.models.role import Role
from sgp_plus.db.models.permission import Permission
from sgp_plus.main import app
from sgp_plus.core.security import hash_password

# Test database
TEST_DATABASE_URL = "postgresql+psycopg://postgres:postgres@localhost:5432/sgp_plus_test"

engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db():
    """Create test database session"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def test_user(db):
    """Usuário sem rbac.manage (só test.read)."""
    perm = Permission(id="test.read", code="test.read", name="Test Read")
    db.add(perm)
    db.flush()

    role = Role(id="test_role", code="test_role", name="Test Role")
    role.permissions = [perm]
    db.add(role)
    db.flush()

    user = User(
        email="test@example.com",
        password_hash=hash_password("password123"),
        is_active=True,
    )
    user.roles = [role]
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture(scope="function")
def client(db):
    """Create test client"""
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()

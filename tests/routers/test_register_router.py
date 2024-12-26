from typing import Any

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock

from fastauth.routers.register import get_register_router
from fastauth.schema.base import BaseSchema


# Mock dependencies
@pytest.fixture
def mock_security(fastauth, fastauth_config):
    fastauth_config.ROUTER_AUTH_DEFAULT_PREFIX = "/auth"
    return fastauth


@pytest.fixture
def mock_manager(auth_manager):
    auth_manager.register = AsyncMock(
        return_value={
            "id": "1",
            "email": "test@example.com",
            "is_active": True,
            "is_verified": False,
        }
    )
    return auth_manager


@pytest.fixture
def app(mock_security):
    app = FastAPI()

    # Mock User Create Schema
    class MockUserCreateSchema(BaseSchema):
        email: str
        password: str

    # Mock User Read Schema
    class MockUserReadSchema(BaseSchema):
        id: str
        email: str
        is_active: bool
        is_verified: bool

    # Include router
    app.include_router(
        get_register_router(
            security=mock_security,
            user_read=MockUserReadSchema,
            user_create=MockUserCreateSchema,
        )
    )
    return app


@pytest.fixture
def test_client(app):
    return TestClient(app)


# Tests for Register Router
def test_register(test_client, mock_manager):
    # Mock data for registration
    register_data = {"email": "test@example.com", "password": "password123"}

    response = test_client.post("/auth/register", json=register_data)

    # Check the response status and returned data
    assert response.status_code == 200
    assert response.json() == {
        "id": "1",
        "email": "test@example.com",
        "is_active": True,
        "is_verified": False,
    }

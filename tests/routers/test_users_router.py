import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock

from fastauth.routers.users import get_users_router

from fastauth.schema.base import BaseSchema


# Mock dependencies
@pytest.fixture
def mock_security(fastauth, fastauth_config):
    fastauth_config.ROUTER_USERS_DEFAULT_PREFIX = "/users"
    return fastauth


@pytest.fixture
def mock_manager(auth_manager):
    auth_manager.get_user = AsyncMock(
        return_value={
            "id": "1",
            "email": "test@example.com",
            "is_active": True,
            "is_verified": True,
        }
    )
    auth_manager._update_user = AsyncMock(
        return_value={
            "id": "1",
            "email": "test@example.com",
            "is_active": True,
            "is_verified": True,
        }
    )
    auth_manager.patch_user = AsyncMock(
        return_value={
            "id": "1",
            "email": "updated@example.com",
            "is_active": True,
            "is_verified": True,
        }
    )
    auth_manager.delete_user = AsyncMock(
        return_value={
            "id": "1",
            "email": "deleted@example.com",
            "is_active": False,
            "is_verified": False,
        }
    )
    return auth_manager


@pytest.fixture
def app(mock_security):
    app = FastAPI()

    # Mock User Read and Update Schema
    class MockUserReadSchema(BaseSchema):
        id: str
        email: str
        is_active: bool
        is_verified: bool

    class MockUserUpdateSchema(BaseSchema):
        email: str
        is_active: bool
        is_verified: bool

    # Include router
    app.include_router(
        get_users_router(
            security=mock_security,
            user_read=MockUserReadSchema,
            user_update=MockUserUpdateSchema,
        )
    )
    return app


@pytest.fixture
def test_client(app):
    return TestClient(app)


# Tests for Users Router
def test_get_me(test_client, mock_manager, token_strategy):
    token_strategy.read_token.return_value = {"type": "access"}
    # Simulate an authenticated user request
    response = test_client.get(
        "/users/me", headers={"Authorization": "Bearer access_token"}
    )
    assert response.status_code == 200
    assert response.json() == {
        "id": "1",
        "email": "test@example.com",
        "is_active": True,
        "is_verified": True,
    }


def test_patch_me(test_client, mock_manager, token_strategy):
    token_strategy.read_token.return_value = {"type": "access"}
    update_data = {
        "email": "test@example.com",
        "is_active": True,
        "is_verified": True,
    }
    response = test_client.patch(
        "/users/me", json=update_data, headers={"Authorization": "Bearer access_token"}
    )
    assert response.status_code == 200
    assert response.json() == {
        "id": "1",
        "email": "test@example.com",
        "is_active": True,
        "is_verified": True,
    }


def test_get_user(test_client, mock_manager):
    user_id = "1"
    response = test_client.get(f"/users/{user_id}")
    assert response.status_code == 200
    assert response.json() == {
        "id": "1",
        "email": "test@example.com",
        "is_active": True,
        "is_verified": True,
    }


def test_update_user(test_client, mock_manager):
    user_id = "1"
    update_data = {
        "email": "updated@example.com",
        "is_active": True,
        "is_verified": True,
    }
    response = test_client.patch(f"/users/{user_id}", json=update_data)
    assert response.status_code == 200
    assert response.json() == {
        "id": "1",
        "email": "updated@example.com",
        "is_active": True,
        "is_verified": True,
    }


def test_delete_user(test_client, mock_manager):
    user_id = "1"
    response = test_client.delete(f"/users/{user_id}")
    assert response.status_code == 200
    assert response.json() == {
        "id": "1",
        "email": "deleted@example.com",
        "is_active": False,
        "is_verified": False,
    }

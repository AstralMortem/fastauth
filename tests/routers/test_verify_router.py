import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock

from fastauth.routers.verification import get_verify_router
from fastauth.schema.base import BaseSchema


# Mock dependencies
@pytest.fixture
def mock_security(fastauth, fastauth_config):
    fastauth_config.ROUTER_AUTH_DEFAULT_PREFIX = "/auth"
    return fastauth


@pytest.fixture
def app(mock_security):
    app = FastAPI()

    # Mock User Read Schema
    class MockUserReadSchema(BaseSchema):
        id: int
        email: str
        is_verified: bool

    # Include router
    app.include_router(
        get_verify_router(security=mock_security, user_read=MockUserReadSchema)
    )
    return app


@pytest.fixture
def test_client(app):
    return TestClient(app)


# Tests for Verify Router
def test_request_verify_token(test_client, auth_manager):
    auth_manager.request_verify = AsyncMock(return_value=None)
    email = "test@example.com"
    response = test_client.post(f"/auth/request-verify-token/{email}")
    assert response.status_code == 200
    assert response.content == b"null"  # No content expected for this endpoint


def test_verify_token(test_client, auth_manager):
    auth_manager.verify = AsyncMock(
        return_value={"id": 1, "email": "test@example.com", "is_verified": True}
    )
    token = "dummy-token"
    response = test_client.post(f"/auth/verify/{token}")
    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "email": "test@example.com",
        "is_verified": True,
    }

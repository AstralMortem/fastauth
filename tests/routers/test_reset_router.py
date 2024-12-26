import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock

from fastauth.routers import get_reset_password_router


# Mock dependencies
@pytest.fixture
def mock_security(fastauth, fastauth_config):
    fastauth_config.ROUTER_AUTH_DEFAULT_PREFIX = "/auth"
    return fastauth


@pytest.fixture
def app(mock_security):
    app = FastAPI()

    # Include router
    app.include_router(get_reset_password_router(security=mock_security))
    return app


@pytest.fixture
def test_client(app):
    return TestClient(app)


# Tests for Reset Password Router
def test_forgot_password(test_client, auth_manager):
    auth_manager.forgot_password.return_value = None

    email = "test@example.com"
    response = test_client.post(f"/auth/forgot-password/{email}")
    assert response.status_code == 200
    assert response.content == b"null"  # No content expected for this endpoint


def test_reset_password(test_client, auth_manager):
    auth_manager.reset_password.return_value = None
    token = "dummy-token"
    new_password = "newPassword123"
    response = test_client.post(
        "/auth/reset-password", json={"token": token, "new_password": new_password}
    )
    assert response.status_code == 200
    assert response.content == b"null"  # No content expected for this endpoint

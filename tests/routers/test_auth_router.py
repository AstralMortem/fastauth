import pytest
from fastapi import FastAPI, status
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock, patch

from fastauth.routers.auth import get_auth_router
from fastauth.fastauth import FastAuth
from fastauth.schema import TokenResponse


# Mock FastAuth for testing
@pytest.fixture
def mock_security():
    mock = MagicMock(spec=FastAuth)
    mock.config.TOKEN_LOCATIONS = ["headers"]
    mock.config.ROUTER_AUTH_DEFAULT_PREFIX = "/auth"
    mock.config.TOKEN_LOGIN_URL = "/login"
    mock.config.TOKEN_LOGOUT_URL = "/logout"
    mock.config.TOKEN_REFRESH_URL = "/refresh"
    mock.config.ENABLE_REFRESH_TOKEN = True
    mock.AUTH_MANAGER.password_login = AsyncMock(
        return_value=TokenResponse(
            access_token="test_access_token",
            refresh_token="test_refresh_token",
        )
    )
    mock.AUTH_MANAGER.get_user = AsyncMock(return_value={"id": "user_id"})
    mock.TOKEN_STRATEGY.write_token = AsyncMock(
        side_effect=["access_token", "refresh_token"]
    )
    mock.TOKEN_STRATEGY.read_token = AsyncMock(return_value={"type": "access"})
    mock.REFRESH_TOKEN = {"sub": "user_id"}
    return mock


@pytest.fixture
def app(mock_security):
    app = FastAPI()
    app.include_router(get_auth_router(mock_security))
    return app


@pytest.fixture
def client(app):
    return TestClient(app)


def test_login(client, mock_security):
    response = client.post(
        "/auth/login",
        data={"username": "testuser", "password": "testpassword"},
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "access_token": "test_access_token",
        "refresh_token": "test_refresh_token",
        "type": "bearer",
    }
    # mock_security.AUTH_MANAGER.password_login.assert_awaited_once()


def test_logout(client, mock_security):
    response = client.post(
        "/auth/logout", headers={"Authorization": "Bearer test_access_token"}
    )
    # print(response.json())
    # assert response.status_code == status.HTTP_200_OK


def test_refresh(client, mock_security):
    response = client.post(
        "/auth/refresh",
        headers={"Authorization": "Bearer test_refresh_token"},
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "access_token": "access_token",
        "refresh_token": "refresh_token",
        "type": "bearer",
    }

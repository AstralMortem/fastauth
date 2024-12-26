import pytest
from fastapi import FastAPI, status, HTTPException
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock, patch, Mock

from fastauth.manager import BaseAuthManager
from fastauth.routers.auth import get_auth_router
from fastauth.fastauth import FastAuth
from fastauth.schema import TokenResponse


# Mock FastAuth for testing
@pytest.fixture
def mock_security(fastauth_config, fastauth):
    fastauth_config.TOKEN_LOCATIONS = ["headers"]
    fastauth_config.ROUTER_AUTH_DEFAULT_PREFIX = "/auth"
    fastauth_config.TOKEN_LOGIN_URL = "/login"
    fastauth_config.TOKEN_LOGOUT_URL = "/logout"
    fastauth_config.TOKEN_REFRESH_URL = "/refresh"
    fastauth_config.ENABLE_REFRESH_TOKEN = True
    return fastauth


@pytest.fixture
def app(mock_security):
    app = FastAPI()
    app.include_router(get_auth_router(mock_security))
    return app


@pytest.fixture
def client(app):
    return TestClient(app)


def test_login(client, auth_manager, mock_security):

    auth_manager.password_login.return_value = TokenResponse(
        access_token="test_access_token", refresh_token="test_refresh_token"
    )

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
    auth_manager.password_login.assert_awaited_once()


def test_logout(client, token_strategy):

    token_strategy.read_token.return_value = {"type": "access"}

    response = client.post(
        "/auth/logout", headers={"Authorization": "Bearer test_access_token"}
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_refresh(client, auth_manager, token_strategy, fastauth_config):
    token_strategy.read_token.return_value = {"type": "refresh"}
    token_strategy.write_token.side_effect = lambda user, type: f"{type}_token"

    auth_manager.get_user = AsyncMock(return_value="User")

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

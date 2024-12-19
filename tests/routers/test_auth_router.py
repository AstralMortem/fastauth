import json
from http.client import responses

import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi import FastAPI, Depends
from fastapi.security import OAuth2PasswordRequestForm
from httpx import AsyncClient
from fastauth.routers.auth import get_auth_router
from fastauth.schema import TokenResponse
from fastauth.fastauth import FastAuth
from fastapi.testclient import TestClient


@pytest.fixture
def mock_config():
    config = MagicMock()
    config.ROUTER_AUTH_DEFAULT_PREFIX = "/auth"
    config.TOKEN_LOGIN_URL = "/login"
    config.TOKEN_LOGOUT_URL = "/logout"
    config.TOKEN_REFRESH_URL = "/refresh"
    config.ENABLE_REFRESH_TOKEN = True
    config.TOKEN_LOCATIONS = ["headers"]
    return config


@pytest.fixture
def mock_security(mock_config):
    security = MagicMock(spec=FastAuth)
    security.config = mock_config
    security.AUTH_MANAGER = AsyncMock()
    security.TOKEN_STRATEGY = AsyncMock()
    security.ACCESS_TOKEN = Depends(lambda: "access-token")
    security.REFRESH_TOKEN = MagicMock(sub="user-id")
    security.AUTH_SERVICE = AsyncMock()
    return security


@pytest.fixture
def client(app, mock_security):
    router = get_auth_router(mock_security)
    app.include_router(router)
    return TestClient(app)


@pytest.mark.asyncio
async def test_login(client, mock_security):
    mock_security.AUTH_MANAGER.password_login = AsyncMock(
        return_value=TokenResponse(
            access_token="access-token", refresh_token="refresh-token"
        )
    )

    response = client.post("/auth/login", data={"username": "test", "password": "test"})
    assert response.status_code == 200

    data = json.loads(response.content)
    assert data["access_token"] == "access-token"
    assert data["refresh_token"] == "refresh-token"

    # mock_security.AUTH_MANAGER.password_login.assert_called_once()


@pytest.mark.asyncio
async def test_logout(client, mock_security):
    response = client.post("/auth/logout")
    assert response.status_code == 204
    assert response.content == b""


@pytest.mark.asyncio
async def test_refresh(client, mock_security):
    mock_security.AUTH_SERVICE.get_user.return_value = MagicMock(id="user-id")
    mock_security.TOKEN_STRATEGY.write_token.side_effect = [
        "new-access-token",
        "new-refresh-token",
    ]

    response = client.post("/auth/refresh")

    assert response.status_code == 200
    assert response.json() == {
        "access_token": "new-access-token",
        "refresh_token": "new-refresh-token",
        "type": "bearer",
    }
    # assert mock_security.AUTH_SERVICE.get_user.assert_called_once_with("user-id")

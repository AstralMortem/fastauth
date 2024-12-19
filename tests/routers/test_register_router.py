from unittest.mock import MagicMock, AsyncMock

import pytest
from fastapi import Depends
from starlette.testclient import TestClient

from fastauth.fastauth import FastAuth
from fastauth.routers import get_register_router
from fastauth.schema import UR_S, UC_S, BaseUserRead, BaseUserCreate


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


class UserRead(BaseUserRead[int]):
    pass


class UserCreate(BaseUserCreate):
    pass


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
    router = get_register_router(mock_security, UserRead, UserCreate)
    app.include_router(router)
    return TestClient(app)


@pytest.mark.asyncio
async def test_register(client, mock_security):
    return_dict = {
        "id": 1,
        "email": "test@test.com",
        "username": "test_user",
        "is_active": True,
        "is_verified": False,
    }
    mock_security.AUTH_MANAGER.register.return_value = return_dict

    response = client.post(
        "/auth/register",
        json={
            "username": "test_user",
            "password": "password123",
            "email": "test@test.com",
        },
    )
    assert response.status_code == 200
    assert response.json() == return_dict
    # mock_security.AUTH_MANAGER.register.assert_called_once_with(mock_user_create)

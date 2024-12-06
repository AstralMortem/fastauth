import pytest
from unittest.mock import MagicMock, AsyncMock
from fastapi import Response
from fastapi.security import APIKeyCookie
from fastauth.backend.transport.cookie import CookieTransport


@pytest.fixture
def mock_config():
    return MagicMock(
        COOKIE_ACCESS_NAME="access_token",
        COOKIE_ACCESS_MAX_AGE=3600,
        COOKIE_REFRESH_NAME="refresh_token",
        COOKIE_REFRESH_MAX_AGE=7200,
        COOKIE_PATH="/",
        COOKIE_DOMAIN="example.com",
        COOKIE_SECURE=True,
        COOKIE_HTTPONLY=True,
        COOKIE_SAMESITE="Lax",
        ENABLE_REFRESH_TOKEN=True,
    )


@pytest.fixture
def cookie_transport(mock_config):
    transport = CookieTransport(mock_config)
    return transport


def test_schema(cookie_transport, mock_config):
    schema = cookie_transport.schema()
    assert isinstance(schema, APIKeyCookie)
    assert schema.model.name == mock_config.COOKIE_ACCESS_NAME


@pytest.mark.asyncio
async def test_get_login_response_with_refresh_token(cookie_transport, mock_config):
    access_token = "access_token_example"
    refresh_token = "refresh_token_example"

    response = await cookie_transport.get_login_response(access_token, refresh_token)

    # Assert response status
    assert response.status_code == 204

    # Assert access_token cookie
    cookies = response.headers.getlist("set-cookie")
    access_cookie = next(
        c for c in cookies if c.startswith(mock_config.COOKIE_ACCESS_NAME)
    )
    assert access_token in access_cookie

    # Assert refresh_token cookie
    refresh_cookie = next(
        c for c in cookies if c.startswith(mock_config.COOKIE_REFRESH_NAME)
    )
    assert refresh_token in refresh_cookie


@pytest.mark.asyncio
async def test_get_login_response_without_refresh_token(cookie_transport, mock_config):
    access_token = "access_token_example"

    response = await cookie_transport.get_login_response(access_token)

    # Assert response status
    assert response.status_code == 204

    # Assert access_token cookie
    cookies = response.headers.getlist("set-cookie")
    access_cookie = next(
        c for c in cookies if c.startswith(mock_config.COOKIE_ACCESS_NAME)
    )
    assert access_token in access_cookie

    # Assert no refresh_token cookie
    with pytest.raises(StopIteration):
        next(c for c in cookies if c.startswith(mock_config.COOKIE_REFRESH_NAME))


@pytest.mark.asyncio
async def test_get_logout_response(cookie_transport, mock_config):
    response = await cookie_transport.get_logout_response()

    # Assert response status
    assert response.status_code == 204

    # Assert access_token cookie is removed
    cookies = response.headers.getlist("set-cookie")
    access_cookie = next(
        c for c in cookies if c.startswith(mock_config.COOKIE_ACCESS_NAME)
    )
    assert "Max-Age=0" in access_cookie

    # Assert refresh_token cookie is removed
    refresh_cookie = next(
        c for c in cookies if c.startswith(mock_config.COOKIE_REFRESH_NAME)
    )
    assert "Max-Age=0" in refresh_cookie

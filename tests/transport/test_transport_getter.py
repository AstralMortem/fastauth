import json
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import Request

from fastauth import exceptions
from fastauth.schema import TokenResponse
from fastauth.transport import (
    TRANSPORT_GETTER,
    _get_token_from_request,
    get_login_response,
    get_logout_response,
)


@pytest.fixture
def mock_config():
    config = MagicMock()
    config.TOKEN_LOCATIONS = ["headers", "cookies"]
    return config


@pytest.fixture
def mock_security(mock_config):
    security = MagicMock()
    security._config = mock_config
    return security


@pytest.fixture
def mock_request():
    return MagicMock(spec=Request)


@pytest.mark.asyncio
async def test_get_login_response(fastauth_instance):
    tokens = TokenResponse(access_token="access-token", refresh_token="refresh-token")
    response = await get_login_response(fastauth_instance, tokens)
    assert tokens.model_dump() == json.loads(response.body)
    assert "access-token" in str(response.headers.raw[2][1])
    assert "refresh-token" in str(response.headers.raw[3][1])


@pytest.mark.asyncio
async def test_get_logout_response(fastauth_instance):
    response = await get_logout_response(fastauth_instance)
    assert response.body == b""
    assert 'access_token_cookie=""' in (str(response.headers.raw[0][1]))
    assert 'refresh_token_cookie=""' in (str(response.headers.raw[1][1]))

    # mock_transport.logout_response.assert_called_once_with(mock_security, mock_response)


@pytest.mark.asyncio
async def test_get_token_from_request(fastauth_config, mock_request):
    mock_bearer_transport = AsyncMock()
    mock_cookie_transport = AsyncMock()

    TRANSPORT_GETTER["headers"] = MagicMock(return_value=mock_bearer_transport)
    TRANSPORT_GETTER["cookies"] = MagicMock(return_value=mock_cookie_transport)

    token_getter = _get_token_from_request(fastauth_config, mock_request)

    # Test valid token from headers
    mock_bearer_transport.schema.return_value = "header-token"
    token = await token_getter(headers="header-token", cookies=None)
    assert token == "header-token"

    # Test valid token from cookies
    mock_cookie_transport.schema.return_value = "cookie-token"
    token = await token_getter(headers=None, cookies="cookie-token")
    assert token == "cookie-token"

    # Test missing token
    with pytest.raises(exceptions.MissingToken):
        await token_getter(headers=None, cookies=None)

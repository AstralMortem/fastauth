from datetime import datetime, timezone, timedelta

import pytest
from unittest.mock import Mock
from fastapi import Depends
from fastauth.fastauth import FastAuth
from fastauth.config import FastAuthConfig
from fastauth.backend.strategies import BaseStrategy
from fastauth.backend.transport import BaseTransport
from fastauth.manager import AuthManagerDependency, BaseAuthManager
from fastauth.schemas import TokenPayload
from fastauth import exceptions


@pytest.fixture
def mock_config():
    return Mock(spec=FastAuthConfig)


@pytest.fixture
def mock_auth_manager():
    return Mock(spec=AuthManagerDependency)


@pytest.fixture
def mock_strategy():
    return Mock(spec=BaseStrategy)


@pytest.fixture
def mock_transport():
    return Mock(spec=BaseTransport)


@pytest.fixture
def fast_auth(mock_config, mock_auth_manager, mock_strategy, mock_transport):
    return FastAuth(mock_config, mock_auth_manager, mock_strategy, mock_transport)


class TestFastAuth:
    pass


@pytest.mark.asyncio
async def test_authenticated_raises_invalid_token_when_type_mismatch(
    fast_auth, mock_strategy
):
    mock_strategy.read_token.return_value = TokenPayload(type="refresh", sub="user_id")
    authenticated = fast_auth.authenticated(token_type="access")

    with pytest.raises(exceptions.InvalidToken) as exc_info:
        await authenticated(token="some_token", strategy=mock_strategy)

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail.startswith("Invalid access token")
    mock_strategy.read_token.assert_called_once_with("some_token")


@pytest.mark.asyncio
async def test_authenticated_raises_invalid_token_when_expired(
    fast_auth, mock_strategy
):
    token = "expired_token"
    token_payload = TokenPayload(
        sub="user123",
        exp=datetime.now(timezone.utc) - timedelta(hours=1),
        type="access",
    )
    mock_strategy.read_token.return_value = token_payload

    authenticated = fast_auth.authenticated()

    with pytest.raises(exceptions.InvalidToken) as exc_info:
        await authenticated(token=token, strategy=mock_strategy)

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail.startswith("Invalid access token: Expired")
    mock_strategy.read_token.assert_called_once_with(token)

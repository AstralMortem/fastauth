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


# @pytest.mark.asyncio
# async def test_current_user_raises_access_denied_when_user_not_active_or_verified(
#     fast_auth, mock_auth_manager
# ):
#     # Arrange
#     fast_auth.config.DEFAULT_CURRENT_USER_IS_ACTIVE = True
#     fast_auth.config.DEFAULT_CURRENT_USER_IS_VERIFIED = True
#     mock_token_payload = Mock(spec=TokenPayload, sub="user_id")
#     mock_user = Mock(is_active=False, is_verified=False)
#     mock_auth_manager.parse_user_id.return_value = "user_id"
#     mock_auth_manager.get_user.return_value = mock_user
#
#     current_user = fast_auth.current_user()
#
#     # Act & Assert
#     with pytest.raises(exceptions.AccessDenied):
#         await current_user(
#             token_payload=mock_token_payload, auth_manager=mock_auth_manager
#         )

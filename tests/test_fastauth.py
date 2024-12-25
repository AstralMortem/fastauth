from datetime import datetime, timedelta, timezone
from typing import Coroutine
from unittest.mock import AsyncMock

import pytest
from fastapi import Response

from fastauth import FastAuth
from fastauth.exceptions import TokenRequired
from fastauth.types import TokenType


@pytest.mark.parametrize("token_type", ("access", "refresh"))
@pytest.mark.asyncio
async def test_create_token(
    token_type, fastauth_instance, fastauth_strategy, fastauth_manager
):
    """Test access token creation."""
    token_string = f"mocked_{token_type}_token"

    fastauth_strategy.write_token = AsyncMock(return_value=token_string)
    fastauth_manager.create_token = AsyncMock(return_value=token_string)
    fastauth_instance.set_token_strategy(AsyncMock(return_value=fastauth_strategy))
    fastauth_instance.set_auth_callback(AsyncMock(return_value=fastauth_manager))

    if token_type == "access":
        token = await fastauth_instance.create_access_token(
            uid="user123", extra={"scope": "read"}
        )
    else:
        token = await fastauth_instance.create_refresh_token(
            uid="user123", extra={"scope": "read"}
        )

    assert token == token_string
    fastauth_manager.create_token.assert_called_once()
    args = fastauth_manager.create_token.call_args
    assert args[0][0] == "user123"
    assert args[1]["token_type"] == token_type
    assert args[1]["extra_data"] == {"scope": "read"}


@pytest.mark.parametrize("token_type", ("access", "refresh"))
def test_set_cookie(token_type, fastauth_instance):
    """Test setting an access token cookie."""
    response = Response()
    token = f"mocked_{token_type}_token"

    if token_type == "access":
        updated_response = fastauth_instance.set_access_cookie(
            token, response, secure=True
        )
    else:
        updated_response = fastauth_instance.set_refresh_cookie(
            token, response, secure=True
        )
    assert f"{token_type}" in updated_response.headers["set-cookie"]
    assert "Secure" in updated_response.headers["set-cookie"]


@pytest.mark.parametrize("refresh", [True, False])
def test_remove_cookies(refresh, fastauth_instance, fastauth_config):
    """Test removing cookies."""
    fastauth_instance.config.ENABLE_REFRESH_TOKEN = refresh
    response = Response()
    updated_response = fastauth_instance.remove_cookies(response)

    access_token = f'{fastauth_config.COOKIE_ACCESS_TOKEN_NAME}=""'
    refresh_token = f'{fastauth_config.COOKIE_REFRESH_TOKEN_NAME}=""'
    cookie = " ".join(updated_response.headers.values())

    assert access_token in cookie
    if refresh:
        assert refresh_token in cookie


@pytest.mark.parametrize("token_type", ("access", "refresh"))
@pytest.mark.asyncio
async def test_token_required(
    token_type: TokenType, fastauth_instance, fastauth_strategy
):
    """Test access token required functionality."""
    token_payload = {
        "sub": "user123",
        "type": token_type,
        "aud": "test-audience",
        "exp": datetime.now(timezone.utc) + timedelta(seconds=3600),
    }
    fastauth_strategy.read_token = AsyncMock(return_value=token_payload)
    fastauth_instance.set_token_strategy(AsyncMock(return_value=fastauth_strategy))

    dependency = fastauth_instance._token_required(type=token_type)
    result = await dependency(strategy=fastauth_strategy, token="mocked_token")
    assert result == token_payload

    with pytest.raises(TokenRequired):
        wrong_type = "access" if token_type == "refresh" else "refresh"
        dependency = fastauth_instance._token_required(type=wrong_type)
        await dependency(strategy=fastauth_strategy, token="mocked_token")


@pytest.mark.parametrize("roles, permissions", [(["admin"], ["write"]), (None, None)])
@pytest.mark.asyncio
async def test_user_required(
    roles,
    permissions,
    fastauth_instance,
    fastauth_user,
    fastauth_manager,
    fastauth_strategy,
):
    """Test user required with roles and permissions."""
    fastauth_manager.get_user = AsyncMock(return_value=fastauth_user)
    fastauth_manager.check_access = AsyncMock(return_value=fastauth_user)

    fastauth_instance.set_auth_callback(AsyncMock(return_value=fastauth_manager))
    fastauth_instance.set_token_strategy(AsyncMock(return_value=fastauth_strategy))

    dependency = fastauth_instance.user_required(roles=roles, permissions=permissions)
    result = await dependency(
        token_payload={
            "sub": "user123",
            "type": "access",
            "aud": "test-audience",
            "exp": datetime.now(timezone.utc),
        },
        auth_manager=fastauth_manager,
    )

    assert result == fastauth_user
    fastauth_manager.get_user.assert_called_once_with("user123", None, None)

    if roles is not None or permissions is not None:

        fastauth_manager.check_access.assert_called_once_with(
            fastauth_user, roles, permissions
        )


@pytest.mark.asyncio
async def test_dependency_aliases(fastauth_instance):
    fastauth_instance.set_auth_callback(AsyncMock())
    fastauth_instance.set_token_strategy(AsyncMock())

    from fastapi.params import Depends

    assert isinstance(fastauth_instance.AUTH_MANAGER, Depends)
    assert isinstance(fastauth_instance.TOKEN_STRATEGY, Depends)
    assert isinstance(fastauth_instance.ACCESS_TOKEN, Depends)
    assert isinstance(fastauth_instance.REFRESH_TOKEN, Depends)
    assert isinstance(fastauth_instance.DEFAULT_USER, Depends)
    assert isinstance(fastauth_instance.ADMIN_REQUIRED, Depends)


@pytest.mark.asyncio
async def test_fastauth_init(fastauth_config):
    security = FastAuth(fastauth_config)

    with pytest.raises(AttributeError):
        assert security._get_auth_callback()

    with pytest.raises(AttributeError):
        assert security._get_strategy_callback()

    security = FastAuth(fastauth_config, AsyncMock(), AsyncMock())

    # assert isinstance(security._get_auth_callback(), Coroutine)
    # assert isinstance(security._get_strategy_callback(), Coroutine)

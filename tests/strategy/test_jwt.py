from datetime import datetime

import pytest
from unittest.mock import patch, Mock
from jwt import DecodeError
from fastauth.types import TokenType
from fastauth import exceptions
from fastauth.strategy.jwt import JWTStrategy


@pytest.fixture
def token_strategy(fastauth_config):
    fastauth_config.JWT_DEFAULT_AUDIENCE = "test-audience"
    fastauth_config.JWT_ACCESS_TOKEN_MAX_AGE = 3600
    fastauth_config.JWT_REFRESH_TOKEN_MAX_AGE = 3600
    return JWTStrategy(config=fastauth_config)


@pytest.mark.asyncio
async def test_read_token_valid(token_strategy):
    token_strategy.encoder.decode_token = Mock(
        return_value={
            "sub": "user-id",
            "type": "access",
            "aud": "test-audience",
            "exp": 1234567890,
        }
    )

    token = "valid-token"
    payload = await token_strategy.read_token(token)

    assert payload.get("sub") == "user-id"
    assert payload.get("type") == "access"
    token_strategy.encoder.decode_token.assert_called_once_with(
        token, audience="test-audience"
    )


@pytest.mark.asyncio
async def test_read_token_invalid(token_strategy):
    token_strategy.encoder.decode_token = Mock(side_effect=DecodeError("Invalid token"))

    token = "invalid-token"
    with pytest.raises(exceptions.InvalidToken) as exc:
        await token_strategy.read_token(token)

    assert "Invalid JWT token" in str(exc.value)
    token_strategy.encoder.decode_token.assert_called_once_with(
        token, audience="test-audience"
    )


@pytest.mark.parametrize("token_type", ("access", "refresh"))
@pytest.mark.asyncio
async def test_write_token(token_type: TokenType, token_strategy):
    token_strategy.encoder.encode_token = Mock(
        return_value=f"encoded-{token_type}-token"
    )

    class User:
        id = "user-id"

    token = await token_strategy.write_token(User, token_type=token_type)

    assert token == f"encoded-{token_type}-token"

    payload = {
        "sub": str(User.id),
        "type": token_type,
        "id": str(User.id),
    }

    # assert token_strategy.encoder.encode_token.assert_called_once_with(
    #     payload, token_type, max_age=3600, audience="test-audience", headers=None
    # )

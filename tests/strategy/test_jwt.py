from datetime import datetime

import pytest
from unittest.mock import patch
from jwt import DecodeError
from fastauth.schema import TokenPayload
from fastauth.types import TokenType
from fastauth import exceptions
from fastauth.strategy.jwt import JWTStrategy


@pytest.fixture
def token_strategy(fastauth_config):
    fastauth_config.JWT_DEFAULT_AUDIENCE = "test-audience"
    fastauth_config.JWT_ACCESS_TOKEN_MAX_AGE = 3600
    fastauth_config.JWT_REFRESH_TOKEN_MAX_AGE = 3600
    return JWTStrategy(config=fastauth_config)


@patch("fastauth.strategy.jwt.JWT")
@pytest.mark.asyncio
async def test_read_token_valid(mock_jwt, token_strategy):
    mock_jwt_instance = mock_jwt.return_value
    mock_jwt_instance.decode_token.return_value = {
        "sub": "user-id",
        "type": "access",
        "aud": "test-audience",
        "exp": 1234567890,
    }

    token = "valid-token"
    payload = await token_strategy.read_token(token)

    assert isinstance(payload, TokenPayload)
    assert payload.sub == "user-id"
    assert payload.type == "access"
    mock_jwt_instance.decode_token.assert_called_once_with(
        token, audience="test-audience"
    )


@patch("fastauth.strategy.jwt.JWT")
@pytest.mark.asyncio
async def test_read_token_invalid(mock_jwt, token_strategy):
    mock_jwt_instance = mock_jwt.return_value
    mock_jwt_instance.decode_token.side_effect = DecodeError("Invalid token")

    token = "invalid-token"
    with pytest.raises(exceptions.InvalidToken) as exc:
        await token_strategy.read_token(token)

    assert "Invalid JWT token" in str(exc.value)
    mock_jwt_instance.decode_token.assert_called_once_with(
        token, audience="test-audience"
    )


@patch("fastauth.strategy.jwt.JWT")
@pytest.mark.parametrize("token_type", ("access", "refresh"))
@pytest.mark.asyncio
async def test_write_token(mock_jwt, token_type: TokenType, token_strategy):
    mock_jwt_instance = mock_jwt.return_value
    mock_jwt_instance.encode_token.return_value = f"encoded-{token_type}-token"

    payload = TokenPayload(
        sub="user-id", type=token_type, aud="test-audience", exp=datetime.now()
    )
    token = await token_strategy.write_token(payload)

    assert token == f"encoded-{token_type}-token"
    mock_jwt_instance.encode_token.assert_called_once_with(
        payload.model_dump(),
        3600,
        audience="test-audience",
    )

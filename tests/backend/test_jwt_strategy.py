import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastauth.schemas import TokenPayload
from fastauth.models import UP
from fastauth.types import TokenType
from fastauth.config import FastAuthConfig
from fastauth import exceptions
from fastauth.backend.strategies import JWTStrategy


@pytest.fixture
def mock_config():
    return FastAuthConfig(
        JWT_SECRET="test_secret",
        JWT_AUDIENCE=["test_audience"],
        JWT_ALGORITHM="HS256",
        JWT_ACCESS_TOKEN_LIFETIME=3600,
        JWT_REFRESH_TOKEN_LIFETIME=7200,
        USER_DATA_IN_REFRESH_TOKEN=True,
    )


@pytest.fixture
def mock_user():
    class MockUser:
        id = 1
        email = "user@example.com"
        username = "testuser"
        is_active = True
        is_verified = True

    return MockUser()


@pytest.fixture
def jwt_strategy(mock_config):
    strategy = JWTStrategy(mock_config)
    return strategy


@pytest.mark.asyncio
@patch("fastauth.backend.strategies.jwt.decode_jwt")
async def test_read_token_valid(mock_decode_jwt, jwt_strategy):
    mock_decode_jwt.return_value = TokenPayload(
        sub="1", aud=["test_audience"], type="access"
    )
    token = "token_header.token_data.token_sign"
    token_payload = await jwt_strategy.read_token(token)
    assert token_payload.sub == "1"
    mock_decode_jwt.assert_called_once_with(
        token,
        jwt_strategy._config.JWT_SECRET,
        jwt_strategy._config.JWT_AUDIENCE,
        [jwt_strategy._config.JWT_ALGORITHM],
    )


@pytest.mark.asyncio
# @patch("fastauth.backend.strategies.jwt.decode_jwt")
async def test_read_token_invalid(jwt_strategy):
    token = "invalid_token"
    with pytest.raises(exceptions.InvalidToken):
        await jwt_strategy.read_token(token)


@pytest.mark.asyncio
@patch("fastauth.backend.strategies.jwt.encode_jwt")
async def test_write_token_access(mock_encode_jwt, jwt_strategy, mock_user):
    mock_encode_jwt.return_value = "encoded_token"
    token = await jwt_strategy.write_token(mock_user, type="access")
    assert token == "encoded_token"
    mock_encode_jwt.assert_called_once()
    assert "email" in mock_encode_jwt.call_args[0][0]
    assert "username" in mock_encode_jwt.call_args[0][0]


@pytest.mark.asyncio
@patch("fastauth.backend.strategies.jwt.encode_jwt")
async def test_write_token_refresh(mock_encode_jwt, jwt_strategy, mock_user):
    mock_encode_jwt.return_value = "encoded_token"
    token = await jwt_strategy.write_token(mock_user, type="refresh")
    assert token == "encoded_token"
    mock_encode_jwt.assert_called_once()
    assert "email" in mock_encode_jwt.call_args[0][0]
    assert "username" in mock_encode_jwt.call_args[0][0]


def test_set_user_fields_default(jwt_strategy, mock_user):
    fields = jwt_strategy.set_user_fields(mock_user)
    assert fields["email"] == "user@example.com"
    assert fields["username"] == "testuser"
    assert fields["is_active"] is True
    assert fields["is_verified"] is True

import datetime
from datetime import timedelta
from unittest.mock import patch

from fastauth.config import FastAuthConfig
from fastauth.utils.jwt_helper import JWT
import pytest


@pytest.fixture
def mock_config():
    return FastAuthConfig(
        JWT_SECRET="secret_key",
        JWT_ALGORITHM="HS256",
        JWT_DEFAULT_AUDIENCE="test_audience",
        JWT_ACCESS_TOKEN_MAX_AGE=3600,
    )


@pytest.fixture
def jwt_service(mock_config):
    return JWT(config=mock_config)


# Test for the decode_token method
@patch("jwt.decode")
def test_decode_token(mock_decode, jwt_service, mock_config):
    # Arrange
    mock_token = "mocked_token"
    mock_payload = {"sub": "user1", "aud": "test_audience", "exp": 1234567890}
    mock_decode.return_value = mock_payload

    # Act
    decoded = jwt_service.decode_token(mock_token, audience="test_audience")

    # Assert
    mock_decode.assert_called_once_with(
        mock_token,
        key=mock_config.JWT_SECRET,
        algorithms=[mock_config.JWT_ALGORITHM],
        audience="test_audience",
    )
    assert decoded == mock_payload


# Test for the encode_token method
@patch("jwt.encode")
def test_encode_token(mock_encode, jwt_service, mock_config):
    # Arrange
    payload = {"sub": "user1", "iat": datetime.datetime.now(datetime.timezone.utc)}
    max_age = 3600
    expected_token = "encoded_token"
    mock_encode.return_value = expected_token

    # Act
    token = jwt_service.encode_token(payload, max_age=max_age)

    # Assert
    mock_encode.assert_called_once_with(
        {
            **payload,
            "aud": mock_config.JWT_DEFAULT_AUDIENCE,
            "exp": payload["iat"] + timedelta(seconds=max_age),
        },
        key=mock_config.JWT_SECRET,
        algorithm=mock_config.JWT_ALGORITHM,
        headers=None,
    )
    assert token == expected_token


# Test for missing exp field in encode_token
@patch("jwt.encode")
def test_encode_token_missing_exp(mock_encode, jwt_service, mock_config):
    # Arrange
    payload = {"sub": "user1", "iat": datetime.datetime.now(datetime.timezone.utc)}
    max_age = 3600
    expected_token = "encoded_token"
    mock_encode.return_value = expected_token

    # Act
    token = jwt_service.encode_token(payload, max_age=max_age)

    # Assert
    # Assert that exp field is added based on max_age
    assert "exp" in mock_encode.call_args[0][0]
    assert mock_encode.call_args[0][0]["exp"] == payload["iat"] + timedelta(
        seconds=max_age
    )
    assert token == expected_token


# Test if audience is added to encode_token if not present in payload
@patch("jwt.encode")
def test_encode_token_audience(mock_encode, jwt_service, mock_config):
    # Arrange
    payload = {"sub": "user1", "iat": datetime.datetime.now(datetime.timezone.utc)}
    max_age = 3600
    expected_token = "encoded_token"
    mock_encode.return_value = expected_token

    # Act
    token = jwt_service.encode_token(
        payload, max_age=max_age, audience="custom_audience"
    )

    # Assert
    assert "aud" in mock_encode.call_args[0][0]
    assert mock_encode.call_args[0][0]["aud"] == "custom_audience"
    assert token == expected_token


# Test the exception if decode_token raises an error
@patch("jwt.decode")
def test_decode_token_error(mock_decode, jwt_service):
    # Arrange
    mock_token = "invalid_token"
    mock_decode.side_effect = Exception("Invalid token")

    # Act & Assert
    with pytest.raises(Exception, match="Invalid token"):
        jwt_service.decode_token(mock_token)

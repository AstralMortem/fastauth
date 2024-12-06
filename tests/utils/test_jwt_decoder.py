import pytest
from datetime import datetime, timedelta, timezone
from pydantic import SecretStr
import jwt
from fastauth.utils.jwt_helper import _get_secret_value, encode_jwt, decode_jwt

# Mock secret and payload
SECRET = "testsecret"
SECRET_STR = SecretStr("testsecret")
PAYLOAD = {"user_id": 1}
AUDIENCE = ["test-audience"]
ALGORITHM = "HS256"


def test_get_secret_value():
    assert _get_secret_value(SECRET) == "testsecret"
    assert _get_secret_value(SECRET_STR) == "testsecret"


def test_encode_jwt_without_expiration():
    token = encode_jwt(PAYLOAD, SECRET, algorithm=ALGORITHM)
    decoded = jwt.decode(token, SECRET, algorithms=[ALGORITHM], audience=None)
    assert decoded["user_id"] == PAYLOAD["user_id"]
    assert "exp" not in decoded


def test_encode_jwt_with_expiration():
    token = encode_jwt(PAYLOAD, SECRET, lifetime_seconds=60, algorithm=ALGORITHM)
    decoded = jwt.decode(token, SECRET, algorithms=[ALGORITHM], audience=None)
    assert decoded["user_id"] == PAYLOAD["user_id"]
    assert "exp" in decoded
    expire_time = datetime.fromtimestamp(decoded["exp"], tz=timezone.utc)
    assert expire_time > datetime.now(timezone.utc)


def test_decode_jwt_valid():
    token = encode_jwt({**PAYLOAD, "aud": AUDIENCE}, SECRET, algorithm=ALGORITHM)
    decoded = decode_jwt(token, SECRET, audience=AUDIENCE, algorithms=[ALGORITHM])
    assert decoded["user_id"] == PAYLOAD["user_id"]


def test_decode_jwt_invalid_audience():
    token = encode_jwt(
        {**PAYLOAD, "aud": ["wrong-audience"]}, SECRET, algorithm=ALGORITHM
    )
    with pytest.raises(jwt.InvalidAudienceError):
        decode_jwt(token, SECRET, audience=AUDIENCE, algorithms=[ALGORITHM])


def test_decode_jwt_invalid_algorithm():
    token = encode_jwt(PAYLOAD, SECRET, algorithm="HS512")
    with pytest.raises(jwt.InvalidAlgorithmError):
        decode_jwt(token, SECRET, audience=None, algorithms=[ALGORITHM])


def test_decode_jwt_expired():
    token = encode_jwt(PAYLOAD, SECRET, lifetime_seconds=-10, algorithm=ALGORITHM)
    with pytest.raises(jwt.ExpiredSignatureError):
        decode_jwt(token, SECRET, audience=None, algorithms=[ALGORITHM])

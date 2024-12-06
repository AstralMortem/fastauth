import json

import pytest
from unittest.mock import MagicMock
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from fastauth.backend.transport import BearerTransport
from fastauth.schemas.token import BearerTokenResponse


@pytest.fixture
def mock_config():
    return MagicMock(
        AUTH_ROUTER_DEFAULT_PREFIX="/auth",
        TOKEN_LOGIN_URL="/login",
    )


@pytest.fixture
def bearer_transport(mock_config):
    transport = BearerTransport(mock_config)
    return transport


@pytest.mark.asyncio
async def test_get_login_response_with_refresh_token(bearer_transport):
    access_token = "access_token_example"
    refresh_token = "refresh_token_example"

    response = await bearer_transport.get_login_response(
        access_token=access_token,
        refresh_token=refresh_token,
    )

    assert isinstance(response, JSONResponse)
    assert response.status_code == 200
    assert json.loads(response.body) == {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "type": "bearer",
    }


@pytest.mark.asyncio
async def test_get_login_response_without_refresh_token(bearer_transport):
    access_token = "access_token_example"

    response = await bearer_transport.get_login_response(
        access_token=access_token,
        refresh_token=None,
    )

    assert isinstance(response, JSONResponse)
    assert response.status_code == 200
    assert json.loads(response.body) == {"access_token": access_token, "type": "bearer"}


@pytest.mark.asyncio
async def test_get_logout_response_raises_not_implemented_error(bearer_transport):
    with pytest.raises(NotImplementedError):
        await bearer_transport.get_logout_response()


def test_schema(bearer_transport, mock_config):
    schema: OAuth2PasswordBearer = bearer_transport.schema()
    assert isinstance(schema, OAuth2PasswordBearer)
    expected_url = "/auth/login"
    assert schema.model.flows.password.tokenUrl == expected_url

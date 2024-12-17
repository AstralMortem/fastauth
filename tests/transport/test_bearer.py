import pytest
from unittest.mock import Mock, AsyncMock
from fastapi.security import OAuth2PasswordBearer
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from fastapi.security.base import SecurityBase
from starlette.datastructures import Headers

from fastauth.schema import TokenResponse
from fastauth.transport.bearer import (
    BearerTransport,
)  # Replace with the actual module path


@pytest.fixture
def bearer_transport(fastauth_config):
    fastauth_config.ROUTER_AUTH_DEFAULT_PREFIX = "/auth"
    fastauth_config.TOKEN_LOGIN_URL = "/token"
    """Fixture for BearerTransport instance."""
    transport = BearerTransport(fastauth_config)
    return transport


@pytest.mark.asyncio
async def test_schema(bearer_transport):
    """Test schema generation for OAuth2PasswordBearer."""
    request = Mock(spec=Request)
    request.headers = Headers({"Authorization": "Bearer test"})

    oauth2_schema = bearer_transport.schema(request, refresh=False)
    # token = await oauth2_schema(request)
    # assert token == "test"

    assert isinstance(oauth2_schema, SecurityBase)

    # assert isinstance(oauth2_schema, OAuth2PasswordBearer)
    assert oauth2_schema.model.flows.password.tokenUrl == "/auth/token"
    print(oauth2_schema.model.flows)


@pytest.mark.asyncio
async def test_login_response_with_custom_response(bearer_transport):
    """Test login_response with a custom response."""
    security_mock = Mock()  # Mocking the FastAuth dependency
    token_response = TokenResponse(access_token="abc123", type="bearer")
    response = Mock(spec=Response)

    # Mock the render method for Response
    response.render = Mock(return_value=b'{"access_token": "abc123", "type": "bearer"}')
    response.init_headers = Mock()

    final_response = await bearer_transport.login_response(
        security=security_mock, content=token_response, response=response
    )

    assert final_response is response
    response.render.assert_called_once_with(
        {"access_token": "abc123", "refresh_token": None, "type": "bearer"}
    )
    response.init_headers.assert_called_once()


@pytest.mark.asyncio
async def test_login_response_with_default_response(bearer_transport):
    """Test login_response with the default JSONResponse."""
    security_mock = Mock()  # Mocking the FastAuth dependency
    token_response = TokenResponse(access_token="abc123", type="bearer")

    final_response = await bearer_transport.login_response(
        security=security_mock, content=token_response
    )

    assert isinstance(final_response, JSONResponse)
    assert (
        final_response.body
        == b'{"access_token":"abc123","refresh_token":null,"type":"bearer"}'
    )
    assert final_response.status_code == 200


@pytest.mark.asyncio
async def test_logout_response_with_custom_response(bearer_transport):
    """Test logout_response with a custom response."""
    security_mock = Mock()  # Mocking the FastAuth dependency
    response = Mock(spec=Response)

    final_response = await bearer_transport.logout_response(
        security=security_mock, response=response
    )

    assert final_response is response


@pytest.mark.asyncio
async def test_logout_response_with_default_response(bearer_transport):
    """Test logout_response with the default response."""
    security_mock = Mock()  # Mocking the FastAuth dependency

    final_response = await bearer_transport.logout_response(security=security_mock)

    assert isinstance(final_response, Response)
    assert final_response.status_code == 204

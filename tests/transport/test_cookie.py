import pytest
from unittest.mock import Mock, AsyncMock
from fastapi.security import APIKeyCookie
from fastapi import Request, Response

from fastauth.transport.cookie import CookieTransport


@pytest.fixture
async def security():
    security = Mock()
    security.set_refresh_cookie = Mock(side_effect=lambda token, res: res)
    security.set_access_cookie = Mock(side_effect=lambda token, res: res)

    return security


@pytest.fixture
def cookie_transport(fastauth_config):
    fastauth_config.COOKIE_ACCESS_TOKEN_NAME = "access_token"
    fastauth_config.COOKIE_REFRESH_TOKEN_NAME = "refresh_token"
    transport = CookieTransport(fastauth_config)
    return transport


@pytest.mark.parametrize("token_type", ("access", "refresh"))
def test_schema_token(token_type, cookie_transport):
    """Test schema for access token."""
    request = Mock(spec=Request)

    schema = cookie_transport.schema(request, refresh=bool(token_type == "refresh"))

    assert isinstance(schema, APIKeyCookie)
    assert schema.model.name == f"{token_type}_token"
    assert not schema.auto_error


#
# @pytest.mark.asyncio
# async def test_login_response_with_custom_response(cookie_transport, security):
#     """Test login_response with a custom response."""
#     token_response = TokenResponse(
#         access_token="abc123", refresh_token="refresh456", type="bearer"
#     )
#     response = Mock(spec=Response)
#
#     final_response = await cookie_transport.login_response(
#         security=security, content=token_response, response=response
#     )
#
#     security.set_access_cookie.assert_called_once_with("abc123", response)
#     security.set_refresh_cookie.assert_called_once_with("refresh456", response)
#     assert final_response is response
#
#
# @pytest.mark.asyncio
# async def test_login_response_with_default_response(cookie_transport, mock_security):
#     """Test login_response without a custom response."""
#     token_response = TokenResponse(
#         access_token="abc123", refresh_token="refresh456", token_type="bearer"
#     )
#
#     final_response = await cookie_transport.login_response(
#         security=mock_security, content=token_response, response=None
#     )
#
#     assert isinstance(final_response, Response)
#     assert final_response.status_code == 204
#     mock_security.set_access_cookie.assert_called_once_with("abc123", final_response)
#     mock_security.set_refresh_cookie.assert_called_once_with(
#         "refresh456", final_response
#     )
#
#
# @pytest.mark.asyncio
# async def test_logout_response_with_custom_response(cookie_transport, mock_security):
#     """Test logout_response with a custom response."""
#     response = Mock(spec=Response)
#
#     final_response = await cookie_transport.logout_response(
#         security=mock_security, response=response
#     )
#
#     mock_security.remove_cookies.assert_called_once_with(response)
#     assert final_response is response
#
#
# @pytest.mark.asyncio
# async def test_logout_response_with_default_response(cookie_transport, mock_security):
#     """Test logout_response with a default response."""
#     final_response = await cookie_transport.logout_response(
#         security=mock_security, response=None
#     )
#
#     assert isinstance(final_response, Response)
#     assert final_response.status_code == 204
#     mock_security.remove_cookies.assert_called_once_with(final_response)

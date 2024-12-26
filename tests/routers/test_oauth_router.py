import pytest
from fastapi import FastAPI, HTTPException, Response
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock, Mock
from httpx_oauth.oauth2 import OAuth2Token
from jwt import DecodeError

from fastauth.routers.oauth import get_oauth_router, OAuth2AuthorizeResponse


# Mock dependencies
@pytest.fixture
def mock_security(fastauth, fastauth_config):
    fastauth_config.ROUTER_AUTH_DEFAULT_PREFIX = "/auth"
    fastauth_config.JWT_DEFAULT_STATE_AUDIENCE = "test_audience"
    fastauth_config.JWT_STATE_TOKEN_MAX_AGE = 3600
    fastauth_config.USER_DEFAULT_ROLE = "user"

    return fastauth


@pytest.fixture
def mock_client():
    client = AsyncMock()
    client.name = "mockclient"
    return client


@pytest.fixture
def app(mock_security, mock_client):
    app = FastAPI()
    router = get_oauth_router(
        security=mock_security,
        client=mock_client,
        redirect_url="http://testserver/callback",
    )
    app.include_router(router)
    return app


@pytest.fixture
def test_client(app):
    return TestClient(app)


def test_authorize_endpoint(test_client, mock_security, mock_client, auth_manager):

    auth_manager.token_encoder = Mock()
    auth_manager.token_encoder.encode_token.return_value = "state_token"

    mock_client.get_authorization_url = AsyncMock(return_value="http://auth-url.com")
    response = test_client.get("/auth/mockclient/authorize")

    assert response.status_code == 200
    assert response.json() == {"authorization_url": "http://auth-url.com"}


def test_callback_endpoint_success(
    test_client, mock_security, mock_client, auth_manager
):
    auth_manager.oauth_login = AsyncMock(return_value={"token": "fake_token"})
    mock_client.get_id_email = AsyncMock(return_value=("account_id", "account_email"))

    auth_manager.token_encoder.decode_token.return_value = True
    auth_manager.oauth_callback.return_value = "User"

    response = test_client.get(
        "/auth/mockclient/callback", params={"state": "mock_state", "code": "123"}
    )

    assert response.status_code == 200
    assert "token" in response.json()


def test_callback_endpoint_failure(
    test_client, mock_security, mock_client, auth_manager
):
    mock_client.get_id_email = AsyncMock(return_value=(None, None))

    response = test_client.get(
        "/auth/mockclient/callback", params={"state": "mock_state", "code": "123"}
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "OAuth don`t provide email"}

    mock_client.get_id_email = AsyncMock(return_value=("token", "token"))
    auth_manager.token_encoder.decode_token.side_effect = DecodeError

    response = test_client.get(
        "/auth/mockclient/callback", params={"state": "mock_state", "code": "123"}
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "Can`t decode token"}


@pytest.mark.parametrize(
    "default_role, correct_role", (("User", "User"), (True, "user"), (False, None))
)
@pytest.mark.asyncio
async def test_oauth_router_default_role(
    default_role, correct_role, mock_security, mock_client, auth_manager
):

    app = FastAPI()
    app.include_router(
        get_oauth_router(
            mock_security,
            mock_client,
            default_role=default_role,
        )
    )
    client = TestClient(app)

    mock_client.get_id_email.return_value = ("token", "token")
    auth_manager.get_role_by_codename.side_effect = lambda role: role
    auth_manager.oauth_callback.side_effect = lambda *args, **kwargs: kwargs.get(
        "default_role"
    )
    auth_manager.oauth_login.side_effect = lambda user, *args: user

    response = client.get(
        "/auth/mockclient/callback", params={"state": "mock_state", "code": "123"}
    )

    assert response.json() == correct_role

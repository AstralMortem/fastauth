from unittest.mock import AsyncMock, Mock, MagicMock

import pytest
from fastapi import APIRouter, FastAPI
from httpx_oauth.oauth2 import BaseOAuth2

from fastauth import FastAuth
from fastauth.routers import FastAuthRouter
from fastauth.schema.base import BaseSchema


@pytest.fixture
def fastauth(fastauth_config):
    return FastAuth(fastauth_config, AsyncMock(), AsyncMock())


@pytest.fixture
def router(fastauth):
    return FastAuthRouter(fastauth)


@pytest.fixture
def mock_schema():
    return type("schema", (BaseSchema,), {})


def test_fastauth_router_class(router, mock_schema):

    assert isinstance(router.get_auth_router(), APIRouter)
    assert isinstance(router.get_register_router(mock_schema, mock_schema), APIRouter)
    assert isinstance(router.get_users_router(mock_schema, mock_schema), APIRouter)
    assert isinstance(
        router.get_roles_router(mock_schema, mock_schema, mock_schema), APIRouter
    )
    assert isinstance(
        router.get_permissions_router(mock_schema, mock_schema, mock_schema), APIRouter
    )
    assert isinstance(router.get_verify_router(mock_schema), APIRouter)
    assert isinstance(router.get_reset_router(), APIRouter)
    assert isinstance(router.get_oauth_router(MagicMock(name="oauth")), APIRouter)


def test_fastauth_router_register(router, mock_schema):

    class App:
        stored_router = []

        def include_router(self, router, **kwargs):
            self.stored_router.append(router)

    app = App()

    SCHEMA = {
        "user": {"read": mock_schema, "create": mock_schema, "update": mock_schema},
        "role": {"read": mock_schema, "create": mock_schema, "update": mock_schema},
        "permission": {
            "read": mock_schema,
            "create": mock_schema,
            "update": mock_schema,
        },
    }

    result = router.register_in_fastapi(app, SCHEMA)

    isinstance(result, App)

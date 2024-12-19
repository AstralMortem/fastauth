from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import FastAPI

from fastauth.manager import BaseAuthManager
from fastauth.repository import UserRepositoryProtocol


@pytest.fixture
def router_security_instance(fastauth_instance, fastauth_manager, fastauth_strategy):
    @fastauth_instance.set_auth_callback
    async def auth_manager(config, **kwargs):
        user_repo = MagicMock(spec=UserRepositoryProtocol)
        return AsyncMock(return_value=BaseAuthManager(config, user_repo))

    @fastauth_instance.set_token_strategy
    async def strategy(config, **kwargs):
        return fastauth_strategy(config)

    return fastauth_instance


@pytest.fixture
def app(fastauth_instance):
    app = FastAPI()
    return app

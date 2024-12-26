from unittest.mock import MagicMock, AsyncMock

import pytest

from fastauth import FastAuth
from fastauth.manager import BaseAuthManager
from fastauth.strategy.base import TokenStrategy
from fastauth.utils.jwt_helper import TokenHelperProtocol
from fastauth.utils.password import PasswordHelperProtocol


@pytest.fixture
def auth_manager():
    auth_manager = MagicMock(spec=BaseAuthManager)
    auth_manager.token_encoder = MagicMock(spec=TokenHelperProtocol)
    auth_manager.password_helper = MagicMock(spec=PasswordHelperProtocol)
    return auth_manager


@pytest.fixture
def token_strategy():
    return MagicMock(spec=TokenStrategy)


@pytest.fixture
def fastauth(fastauth_config, auth_manager, token_strategy):
    mock = FastAuth(
        fastauth_config,
        AsyncMock(return_value=auth_manager),
        AsyncMock(return_value=token_strategy),
    )
    return mock

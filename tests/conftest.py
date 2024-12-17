from unittest.mock import Mock, AsyncMock

import pytest
from fastauth._callback import _FastAuthCallback
from fastauth.fastauth import FastAuth
from fastauth.config import FastAuthConfig
from fastauth.manager import BaseAuthManager
from fastauth.repository import UserRepositoryProtocol
from fastauth.strategy.base import TokenStrategy


@pytest.fixture
def fastauth_config():
    return FastAuthConfig()


@pytest.fixture
def fastauth_callback(fastauth_config):
    instance = _FastAuthCallback()
    instance._config = fastauth_config  # Set the config for the callback.
    return instance


@pytest.fixture
def fastauth_strategy():
    strategy = AsyncMock(spec=TokenStrategy)
    return strategy


@pytest.fixture
def fastauth_user():
    return Mock()


@pytest.fixture
def fastauth_user_repository():
    return Mock(spec=UserRepositoryProtocol)


@pytest.fixture
def fastauth_manager():
    return AsyncMock(spec=BaseAuthManager)


@pytest.fixture
def fastauth_instance(fastauth_config):
    return FastAuth(fastauth_config)

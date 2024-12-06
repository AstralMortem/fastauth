import pytest
from unittest.mock import Mock
from fastapi import Depends
from fastauth.fastauth import FastAuth
from fastauth.config import FastAuthConfig
from fastauth.backend.strategies import BaseStrategy
from fastauth.backend.transport import BaseTransport
from fastauth.manager import AuthManagerDependency, BaseAuthManager
from fastauth.schemas import TokenPayload
from fastauth import exceptions


@pytest.fixture
def mock_config():
    return Mock(spec=FastAuthConfig)


@pytest.fixture
def mock_auth_manager():
    return Mock(spec=AuthManagerDependency)


@pytest.fixture
def mock_strategy():
    return Mock(spec=BaseStrategy)


@pytest.fixture
def mock_transport():
    return Mock(spec=BaseTransport)


@pytest.fixture
def fast_auth(mock_config, mock_auth_manager, mock_strategy, mock_transport):
    return FastAuth(mock_config, mock_auth_manager, mock_strategy, mock_transport)


class TestFastAuth:
    pass

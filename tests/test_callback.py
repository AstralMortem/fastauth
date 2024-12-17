import inspect
from unittest.mock import MagicMock
import pytest
from fastapi import Depends
from pydantic_settings import BaseSettings
from fastauth.config import FastAuthConfig
from fastauth.manager import BaseAuthManager
from fastauth.strategy.base import TokenStrategy
from fastauth.utils.injector import injectable


def test_set_auth_callback(fastauth_callback):
    @fastauth_callback.set_auth_callback
    async def mock_auth_callback(config: FastAuthConfig):
        return MagicMock(spec=BaseAuthManager)

    assert fastauth_callback._is_auth_callback_set
    retrieved_callback = fastauth_callback._get_auth_callback()
    assert inspect.iscoroutinefunction(retrieved_callback)


@pytest.mark.asyncio
async def test_auth_callback_execution(fastauth_callback):
    @fastauth_callback.set_auth_callback
    async def mock_auth_callback(config: FastAuthConfig):
        return MagicMock(spec=BaseAuthManager)

    retrieved_callback = fastauth_callback._get_auth_callback()
    result = await retrieved_callback()
    assert isinstance(result, BaseAuthManager)


def test_set_token_strategy_callback(fastauth_callback):
    @fastauth_callback.set_token_strategy
    async def mock_strategy_callback(config: FastAuthConfig):
        return MagicMock(spec=TokenStrategy)

    assert fastauth_callback._is_token_strategy_callback_set
    retrieved_callback = fastauth_callback._get_strategy_callback()
    assert inspect.iscoroutinefunction(retrieved_callback)


@pytest.mark.asyncio
async def test_token_strategy_callback_execution(fastauth_callback):
    async def mock_strategy_callback(config: FastAuthConfig):
        return MagicMock(spec=TokenStrategy)

    fastauth_callback.set_token_strategy(mock_strategy_callback)
    retrieved_callback = fastauth_callback._get_strategy_callback()
    result = await retrieved_callback()
    assert isinstance(result, TokenStrategy)


def test_auth_callback_not_set_error(fastauth_callback):
    with pytest.raises(AttributeError, match="Auth callback not set"):
        fastauth_callback._get_auth_callback()


def test_token_strategy_not_set_error(fastauth_callback):
    with pytest.raises(AttributeError, match="Token strategy not set"):
        fastauth_callback._get_strategy_callback()


def test_build_new_signature(fastauth_callback):
    async def mock_callable(param1: int, param2: str = Depends()):
        pass

    sig = fastauth_callback._build_new_signature(mock_callable)
    assert isinstance(sig, inspect.Signature)
    assert "param2" in sig.parameters


@pytest.mark.asyncio
async def test_token_strategy_extra_dependency(fastauth_callback):
    async def dependency():
        return "dependency"

    @fastauth_callback.set_token_strategy
    async def mock_strategy_callback(
        config: FastAuthConfig, dep: str = Depends(dependency)
    ):
        return MagicMock(spec=TokenStrategy, dep=dep)

    callback = fastauth_callback._get_strategy_callback()

    instance = injectable(callback)  # manualy resolve dependencies
    strategy = await instance()
    assert strategy.dep == "dependency"


@pytest.mark.asyncio
async def test_auth_manager_extra_dependency(fastauth_callback):
    async def dependency():
        return "dependency"

    @fastauth_callback.set_auth_callback
    async def mock_auth_manager_callback(
        config: FastAuthConfig, dep: str = Depends(dependency)
    ):
        return MagicMock(spec=BaseAuthManager, dep=dep)

    callback = fastauth_callback._get_auth_callback()

    instance = injectable(callback)  # manualy resolve dependencies
    strategy = await instance()
    assert strategy.dep == "dependency"

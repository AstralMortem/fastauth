import logging

import pytest
from fastapi import Depends
from typing import Any

# Assume the injectable function and related imports are defined in a module named `injector`
from fastauth.utils.injector import (
    injectable,
    DependencyError,
    _SOLVED_DEPENDENCIES,
    logger,
)


# Mock dependencies
def dependency_a() -> str:
    return "dependency_a_value"


def dependency_b(dep_a: str = Depends(dependency_a)) -> str:
    return f"{dep_a}_dependency_b_value"


# Sync function with dependencies
@injectable
def sync_function(dep_b: str = Depends(dependency_b)) -> str:
    return f"sync_{dep_b}"


# Async function with dependencies
@injectable
async def async_function(dep_b: str = Depends(dependency_b)) -> str:
    return f"async_{dep_b}"


def test_injectable_sync_function():
    """Test the injectable decorator with a synchronous function."""
    result = sync_function()
    assert result == "sync_dependency_a_value_dependency_b_value"


@pytest.mark.asyncio
async def test_injectable_async_function():
    """Test the injectable decorator with an asynchronous function."""
    result = await async_function()
    assert result == "async_dependency_a_value_dependency_b_value"


def test_dependency_cache():
    """Test the dependency caching mechanism."""
    _SOLVED_DEPENDENCIES.clear()
    result_1 = sync_function()
    result_2 = sync_function()
    # Ensure the cached value is reused
    assert result_1 == result_2
    assert len(_SOLVED_DEPENDENCIES) > 0


def test_injectable_with_dependency_error():
    """Test the injectable decorator when a dependency error occurs."""

    def failing_dependency() -> Any:
        raise DependencyError("Failed to resolve dependency")

    @injectable
    def function_with_error(dep: Any = Depends(failing_dependency)) -> str:
        return "This should never be returned"

    with pytest.raises(DependencyError):
        function_with_error()


def test_injectable_with_custom_errors_handling(caplog):
    """Test if dependency resolution errors are logged properly."""

    def error_prone_dependency() -> Any:
        raise ValueError("Intentional error for testing")

    @injectable
    def function_with_logging(dep: Any = Depends(error_prone_dependency)) -> str:
        return "This should never be reached"

    with caplog.at_level(logging.INFO):
        with pytest.raises(ValueError):
            function_with_logging()

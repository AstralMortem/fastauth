import pytest
from fastapi import Depends
from fastapi.params import Depends as DependsClass

from fastauth.utils.injector import injectable, DependencyError, _SOLVED_DEPENDENCIES


# def mock_db_connection():
#     return "Mocked DB Connection"
#
#
# async def my_function(db_connection: str = Depends(mock_db_connection)):
#     return db_connection
#
#
# @pytest.mark.asyncio
# async def test_dependency_call():
#     result = await my_function()
#     assert isinstance(result, DependsClass)
#
#
# @pytest.mark.asyncio
# async def test_injectable_decorator():
#
#     @injectable
#     async def wrapped(func=Depends(my_function)):
#         return func
#
#     result = await wrapped()
#     assert result == "Mocked DB Connection"
#
#
# @pytest.mark.asyncio
# async def test_injectable_decorator_alias():
#     injected = injectable(my_function)
#     assert await injected() == "Mocked DB Connection"


async def async_dependency():
    return "async_result"


def sync_dependency():
    return "sync_result"


# Test functions to wrap
@injectable
async def async_func(dep: str = Depends(async_dependency)):
    return f"Async Function: {dep}"


@injectable
def sync_func(dep: str = Depends(sync_dependency)):
    return f"Sync Function: {dep}"


@pytest.mark.asyncio
async def test_async_injectable():
    # Test async function with injectable
    result = await async_func()
    assert result == "Async Function: async_result"


def test_sync_injectable():
    # Test sync function with injectable
    result = sync_func()
    assert result == "Sync Function: sync_result"


def test_injectable_cache():
    # Ensure caching works
    _SOLVED_DEPENDENCIES.clear()
    sync_func()
    assert len(_SOLVED_DEPENDENCIES) > 0


def test_dependency_error():
    # Ensure DependencyError is raised correctly
    with pytest.raises(DependencyError):

        @injectable
        def faulty_func(
            dep: str = Depends(
                lambda: (_ for _ in ()).throw(
                    DependencyError("Simulated dependency failure")
                )
            ),
        ):
            return dep

        faulty_func()

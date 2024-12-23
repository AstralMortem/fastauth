import pytest
from fastapi import Depends
from fastapi.params import Depends as DependsClass

from fastauth.utils.injector import injectable


def mock_db_connection():
    return "Mocked DB Connection"


async def my_function(db_connection: str = Depends(mock_db_connection)):
    return db_connection


@pytest.mark.asyncio
async def test_dependency_call():
    result = await my_function()
    assert isinstance(result, DependsClass)


@pytest.mark.asyncio
async def test_injectable_decorator():

    @injectable
    async def wrapped(func=Depends(my_function)):
        return func

    result = await wrapped()
    assert result == "Mocked DB Connection"


@pytest.mark.asyncio
async def test_injectable_decorator_alias():
    injected = injectable(my_function)
    assert await injected() == "Mocked DB Connection"

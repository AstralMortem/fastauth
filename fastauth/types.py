from typing import Callable, TypeVar, Union, Literal
from collections.abc import AsyncGenerator, AsyncIterator, Coroutine, Generator


RETURN_TYPE = TypeVar("RETURN_TYPE")

DependencyCallable = Callable[
    ...,
    Union[
        RETURN_TYPE,
        Coroutine[None, None, RETURN_TYPE],
        AsyncGenerator[RETURN_TYPE, None],
        Generator[RETURN_TYPE, None, None],
        AsyncIterator[RETURN_TYPE],
    ],
]

TokenType = Literal["access", "refresh", "reset", "verify", "state"]

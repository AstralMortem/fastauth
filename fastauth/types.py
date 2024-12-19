from typing import (
    Literal,
    Union,
    Sequence,
    TypeVar,
    Callable,
    Coroutine,
    AsyncGenerator,
    Generator,
    AsyncIterator,
)

TokenType = Literal["access", "refresh"]
StringOrSequence = Union[str, Sequence[str]]
TokenLocations = Literal["headers", "cookies"]


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

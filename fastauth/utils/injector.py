import asyncio
import inspect
import logging
from collections.abc import Callable, Coroutine
from contextlib import AsyncExitStack
from functools import wraps
from typing import Any, TypeVar, cast

from fastapi import Request
from fastapi.dependencies.models import Dependant
from fastapi.dependencies.utils import get_dependant, solve_dependencies

logger = logging.getLogger(__name__)
T = TypeVar("T")
_SOLVED_DEPENDENCIES: dict[tuple[Callable[..., Any], tuple[str]], Any] = {}


class DependencyError(Exception):
    """Exception raised for errors during dependency injection."""


def injectable(  # noqa: C901
    func: Callable[..., T] | Callable[..., Coroutine[Any, Any, T]] | None = None,
    *,
    use_cache: bool = True,
) -> Callable[..., T] | Callable[..., Coroutine[Any, Any, T]]:
    """A decorator to enable FastAPI-style dependency injection for any function (sync or async).

    This allows dependencies defined with FastAPI's Depends mechanism to be automatically
    resolved and injected into CLI tools or other components, not just web endpoints.

    Args:
        func: The function to be wrapped, enabling dependency injection.
        use_cache: Whether to use the dependency cache for the arguments a.k.a sub-dependencies.

    Returns:
        The wrapped function with dependencies injected.

    Raises:
        ValueError: If the dependant.call is not a callable function.
        DependencyError: If an error occurs during dependency resolution.
    """

    def _impl(
        func: Callable[..., T] | Callable[..., Coroutine[Any, Any, T]],
    ) -> Callable[..., T] | Callable[..., Coroutine[Any, Any, T]]:
        is_async = inspect.iscoroutinefunction(func)
        dependency_cache = _SOLVED_DEPENDENCIES if use_cache else None

        async def resolve_dependencies(
            dependant: Dependant,
        ) -> tuple[dict[str, Any], list[Any] | None]:
            fake_request = Request({"type": "http", "headers": [], "query_string": ""})
            async with AsyncExitStack() as stack:
                solved_result = await solve_dependencies(
                    request=fake_request,
                    dependant=dependant,
                    async_exit_stack=stack,
                    embed_body_fields=False,
                    dependency_cache=dependency_cache,
                )
                dep_kwargs = solved_result.values  # noqa: PD011
                if dependency_cache is not None:
                    dependency_cache.update(solved_result.dependency_cache)

            return dep_kwargs, solved_result.errors

        def handle_errors(errors: list[Any] | None) -> None:
            if errors:
                error_details = "\n".join(str(error) for error in errors)
                logger.info(f"Dependency resolution errors: {error_details}")

        def validate_dependant(dependant: Dependant) -> None:
            if dependant.call is None or not callable(dependant.call):
                msg = "The dependant.call attribute must be a callable."
                raise ValueError(msg)

        @wraps(func)
        async def async_call_with_solved_dependencies(*args: Any, **kwargs: Any) -> T:  # noqa: ANN401
            dependant = get_dependant(path="command", call=func)
            validate_dependant(dependant)
            deps, errors = await resolve_dependencies(dependant)
            handle_errors(errors)

            return await cast(Callable[..., Coroutine[Any, Any, T]], dependant.call)(
                *args, **{**deps, **kwargs}
            )

        @wraps(func)
        def sync_call_with_solved_dependencies(*args: Any, **kwargs: Any) -> T:  # noqa: ANN401
            dependant = get_dependant(path="command", call=func)
            validate_dependant(dependant)
            deps, errors = asyncio.run(resolve_dependencies(dependant))
            handle_errors(errors)

            return cast(Callable[..., T], dependant.call)(*args, **{**deps, **kwargs})

        return (
            async_call_with_solved_dependencies
            if is_async
            else sync_call_with_solved_dependencies
        )

    if func is None:
        return _impl  # type: ignore  # noqa: PGH003
    return _impl(func)

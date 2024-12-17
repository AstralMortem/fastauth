import inspect
from typing import Callable, Awaitable, Optional, List
from fastapi.params import Depends as DependsClass
from makefun import with_signature
from fastauth.config import FastAuthConfig
from fastauth.manager import BaseAuthManager
from fastauth.strategy.base import TokenStrategy


class _FastAuthCallback:
    _config: FastAuthConfig

    def __init__(self):
        self._auth_callback: Optional[Callable[..., Awaitable[BaseAuthManager]]] = None
        self._strategy_callback: Optional[Callable[..., Awaitable[TokenStrategy]]] = (
            None
        )

    @property
    def _is_auth_callback_set(self) -> bool:
        return self._auth_callback is not None

    @property
    def _is_token_strategy_callback_set(self) -> bool:
        return self._strategy_callback is not None

    def set_auth_callback(self, callback: Callable[..., Awaitable[BaseAuthManager]]):
        sig = self._build_new_signature(callback)

        @with_signature(sig)
        async def wrapped(**kwargs):
            return await callback(self._config, **kwargs)

        self._auth_callback = wrapped

    def set_token_strategy(self, callback: Callable[..., Awaitable[TokenStrategy]]):
        sig = self._build_new_signature(callback)

        @with_signature(sig)
        async def wrapped(**kwargs):
            return await callback(self._config, **kwargs)

        self._strategy_callback = wrapped

    def _get_strategy_callback(self) -> Callable[..., Awaitable[TokenStrategy]]:
        if not self._is_token_strategy_callback_set:
            raise AttributeError("Token strategy not set")
        return self._strategy_callback

    def _get_auth_callback(self):
        if not self._is_auth_callback_set:
            raise AttributeError("Auth callback not set")
        return self._auth_callback

    def _build_new_signature(self, callable: Callable):
        new_params: List[inspect.Parameter] = []
        inspected = inspect.signature(callable)
        for name, param in inspected.parameters.items():
            if isinstance(param.default, DependsClass):
                new_params.append(
                    inspect.Parameter(
                        name=name,
                        annotation=param.annotation,
                        kind=inspect.Parameter.POSITIONAL_OR_KEYWORD,
                        default=param.default,
                    )
                )

        return inspect.Signature(new_params)

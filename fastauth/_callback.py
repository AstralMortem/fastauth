import inspect

from fastapi.params import Depends as DependsClass
from makefun import with_signature

from fastauth.config import FastAuthConfig
from fastauth.manager import AuthManagerDependency
from fastauth.strategy.base import TokenStrategyDependency
from fastauth.types import DependencyCallable


class _FastAuthCallback:
    _config: FastAuthConfig

    def __init__(self):
        self._auth_callback: AuthManagerDependency | None = None
        self._strategy_callback: TokenStrategyDependency | None = None

    @property
    def _is_auth_callback_set(self) -> bool:
        """Check if auth manager callback set"""
        return self._auth_callback is not None

    @property
    def _is_token_strategy_callback_set(self) -> bool:
        """Check if token strategy callback set"""
        return self._strategy_callback is not None

    def set_auth_callback(self, callback: AuthManagerDependency):
        """
        Set async callable with BaseAuthManager instance. Wraps it @with_signature decorator to pass Depends args on higher level
        :param callback: Async callable with BaseAuthManager instance
        """
        sig = self._build_new_signature(callback)

        @with_signature(sig)
        async def wrapped(**kwargs):
            return await callback(self._config, **kwargs)

        self._auth_callback = wrapped

    def set_token_strategy(self, callback: TokenStrategyDependency):
        """
        Set async callable with TokenStrategy instance. Wraps it @with_signature decorator to pass Depends args on higher level
        :param callback: Async callable with TokenStrategy instance
        """
        sig = self._build_new_signature(callback)

        @with_signature(sig)
        async def wrapped(**kwargs):
            return await callback(self._config, **kwargs)

        self._strategy_callback = wrapped

    def _get_strategy_callback(self) -> TokenStrategyDependency:
        """
        Check if token strategy set, return callable if set
        :raise AttributeError("Token strategy not set")
        """

        if not self._is_token_strategy_callback_set:
            msg = "Token strategy not set"
            raise AttributeError(msg)
        return self._strategy_callback

    def _get_auth_callback(self):
        """
        Check if BaseAuthManager callback set, return callable if set
        :raise AttributeError("Auth callback not set")
        """
        if not self._is_auth_callback_set:
            msg = "Auth callback not set"
            raise AttributeError(msg)
        return self._auth_callback

    def _build_new_signature(self, callable: DependencyCallable):
        """
        Get signature from callable and pass it to new signature
        :param callable: Async callable
        :return: new Signature with new params
        """

        new_params: list[inspect.Parameter] = []
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

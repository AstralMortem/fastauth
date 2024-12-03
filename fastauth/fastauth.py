from collections.abc import Callable
from inspect import Signature, Parameter
from typing import Type, cast, List, Optional
from fastapi import Depends, status, HTTPException
from makefun import with_signature
from sqlalchemy.util import await_only

from fastauth.backend.strategies import BaseStrategy
from fastauth.backend.transport import BaseTransport
from fastauth.config import FastAuthConfig
from fastauth.manager import AuthManagerDependency, BaseAuthManager
from fastauth.schemas import TokenPayload
from fastauth.types import TokenType


class FastAuth:

    def __init__(
        self,
        config: FastAuthConfig,
        auth_manager: AuthManagerDependency,
        strategy: Type[BaseStrategy],
        transport: Type[BaseTransport],
    ):
        self._config = config
        self._manager_dep = auth_manager
        self._strategy = strategy(config)
        self._transport = transport(config)

    @property
    def config(self):
        return self._config

    @property
    def get_manager(self):
        return self._manager_dep

    @property
    def get_strategy(self):
        return lambda: self._strategy

    @property
    def transport(self):
        return self._transport

    def authenticated(self, token_type: TokenType = "access"):
        sig = self._get_authenticated_call_signature()

        @with_signature(sig)
        async def _authenticated(**kwargs):
            token = kwargs.get("token")
            strategy: BaseStrategy = kwargs.get("strategy")

            token_payload: TokenPayload = await strategy.read_token(token)
            if token_payload.type != token_type:
                raise HTTPException(
                    status.HTTP_401_UNAUTHORIZED,
                    f"Invalid Token: {token_type} token is required",
                )

            return token_payload

        return _authenticated

    def current_user(
        self,
        roles: Optional[List[str]] = None,
        permissions: Optional[List[str]] = None,
        is_active: bool = True,
        is_verified: bool = True,
    ):
        sig = self._get_user_call_signature(self.authenticated())

        @with_signature(sig)
        async def _current_user(**kwargs):
            token_payload: TokenPayload = kwargs.get("token_payload")
            manager: BaseAuthManager = kwargs.get("auth_manager")

            not_allowed = HTTPException(status.HTTP_403_FORBIDDEN, "Access denied")
            user_id = manager.parse_user_id(token_payload.sub)
            user = await manager.get_user(user_id)
            if user.is_active != is_active or user.is_verified != is_verified:
                raise not_allowed

            if roles or permissions:
                # todo: implement role and permission check
                pass

            return user

        return _current_user

    def _get_authenticated_call_signature(self) -> Signature:
        parameters: list[Parameter] = [
            Parameter(
                name="strategy",
                kind=Parameter.POSITIONAL_OR_KEYWORD,
                default=Depends(cast(Callable, self.get_strategy)),
            ),
            Parameter(
                name="token",
                kind=Parameter.POSITIONAL_OR_KEYWORD,
                default=Depends(cast(Callable, self.transport.schema())),
            ),
        ]
        return Signature(parameters)

    def _get_user_call_signature(self, authenticated):
        parameters: list[Parameter] = [
            Parameter(
                name="auth_manager",
                kind=Parameter.POSITIONAL_OR_KEYWORD,
                default=Depends(self.get_manager),
                annotation=BaseAuthManager,
            ),
            Parameter(
                name="token_payload",
                kind=Parameter.POSITIONAL_OR_KEYWORD,
                default=Depends(authenticated),
                annotation=TokenPayload,
            ),
        ]
        return Signature(parameters)

    # property section

    @property
    def REFRESH_REQUIRED(self) -> TokenPayload:
        return Depends(self.authenticated(token_type="refresh"))

    @property
    def ACCESS_REQUIRED(self) -> TokenPayload:
        return Depends(self.authenticated())

    @property
    def USER_REQUIRED(self):
        return Depends(self.current_user())

    @property
    def ADMIN_REQUIRED(self):
        return Depends(self.current_user(roles=self.config.DEFAULT_ADMIN_ROLES))

    @property
    def AUTH_MANAGER(self):
        return Depends(self._manager_dep)

    @property
    def STRATEGY(self):
        return Depends(lambda: self._strategy)

    @property
    def TRANSPORT(self):
        return self._transport

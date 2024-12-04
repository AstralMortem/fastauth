from collections.abc import Callable
from inspect import Signature, Parameter
from typing import Type, cast, List, Optional
from fastapi import Depends
from makefun import with_signature
from typing_extensions import Generic

from fastauth.backend.strategies import BaseStrategy
from fastauth.backend.transport import BaseTransport
from fastauth.config import FastAuthConfig
from fastauth.manager import AuthManagerDependency, BaseAuthManager
from fastauth.models import ID, UP, RP, PP, OAP
from fastauth.schemas import TokenPayload
from fastauth.types import TokenType
from fastauth import exceptions


class FastAuth(Generic[UP, ID, RP, PP, OAP]):

    def __init__(
        self,
        config: FastAuthConfig,
        auth_manager: AuthManagerDependency[UP, ID, RP, PP, OAP],
        strategy: Type[BaseStrategy[UP]],
        transport: Type[BaseTransport],
    ):
        self._config = config
        self._manager_dep = auth_manager
        self._strategy = strategy(config)
        self._transport = transport(config)

    @property
    def config(self):
        return self._config

    def authenticated(self, token_type: TokenType = "access"):
        sig = self._get_authenticated_call_signature()

        @with_signature(sig)
        async def _authenticated(**kwargs):
            token = kwargs.get("token")
            strategy: BaseStrategy[UP] = kwargs.get("strategy")

            token_payload: TokenPayload = await strategy.read_token(token)
            if token_payload.type != token_type:
                raise exceptions.InvalidToken(token_type)

            return token_payload

        return _authenticated

    def current_user(
        self,
        roles: Optional[List[str]] = None,
        permissions: Optional[List[str]] = None,
        is_active: Optional[bool] = None,
        is_verified: Optional[bool] = None,
    ):
        sig = self._get_user_call_signature(self.authenticated())

        is_user_active = (
            is_active if is_active else self.config.DEFAULT_CURRENT_USER_IS_ACTIVE
        )
        is_user_verified = (
            is_verified if is_verified else self.config.DEFAULT_CURRENT_USER_IS_VERIFIED
        )

        @with_signature(sig)
        async def _current_user(**kwargs):
            token_payload: TokenPayload = kwargs.get("token_payload")
            manager: BaseAuthManager[UP, ID, RP, PP, OAP] = kwargs.get("auth_manager")

            user_id = manager.parse_user_id(token_payload.sub)
            user = await manager.get_user(user_id)
            if user.is_active != is_user_active or user.is_verified != is_user_verified:
                raise exceptions.AccessDenied

            if (roles or permissions) and self.config.ENABLE_RBAC:
                has_access = await manager.authorize_user(user, roles, permissions)
                if not has_access:
                    raise exceptions.AccessDenied
            return user

        return _current_user

    def _get_authenticated_call_signature(self) -> Signature:
        parameters: list[Parameter] = [
            Parameter(
                name="strategy",
                kind=Parameter.POSITIONAL_OR_KEYWORD,
                default=self.STRATEGY,
            ),
            Parameter(
                name="token",
                kind=Parameter.POSITIONAL_OR_KEYWORD,
                default=Depends(cast(Callable, self.TRANSPORT.schema())),
            ),
        ]
        return Signature(parameters)

    def _get_user_call_signature(self, authenticated):
        parameters: list[Parameter] = [
            Parameter(
                name="auth_manager",
                kind=Parameter.POSITIONAL_OR_KEYWORD,
                default=self.AUTH_MANAGER,
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
    def USER_REQUIRED(self) -> UP:
        return Depends(self.current_user(roles=self.config.DEFAULT_USER_ROLES))

    @property
    def ADMIN_REQUIRED(self) -> UP:
        return Depends(self.current_user(roles=self.config.DEFAULT_ADMIN_ROLES))

    @property
    def AUTH_MANAGER(self) -> BaseAuthManager[UP, ID, RP, PP, OAP]:
        return Depends(self._manager_dep)

    @property
    def STRATEGY(self) -> BaseStrategy[UP]:
        return Depends(lambda: self._strategy)

    @property
    def TRANSPORT(self) -> BaseTransport:
        return self._transport

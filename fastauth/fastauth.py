from inspect import Parameter, Signature
from typing import Dict, Optional, List, Generic, Literal, Any
from fastapi import Response, Depends
from fastapi.openapi.models import SecurityBase
from makefun import with_signature
from fastauth.manager import BaseAuthManager
from fastauth.strategy.base import TokenStrategy, TokenStrategyDependency
from fastauth.types import TokenType
from fastauth import exceptions
from fastauth._callback import _FastAuthCallback
from fastauth.transport import _get_token_from_request
from fastauth.config import FastAuthConfig
from fastauth.utils.injector import injectable
from fastauth.models import UP, ID, RP, PP, OAP

from fastauth.manager import AuthManagerDependency


class FastAuth(Generic[UP, ID, RP, PP, OAP], _FastAuthCallback):
    def __init__(
        self,
        config: FastAuthConfig,
        auth_manager_dependency: Optional[
            AuthManagerDependency[UP, ID, RP, PP, OAP]
        ] = None,
        token_strategy_dependency: Optional[TokenStrategyDependency[UP, ID]] = None,
    ):
        self._config = config
        super().__init__()

        if auth_manager_dependency:
            self.set_auth_callback(auth_manager_dependency)

        if token_strategy_dependency:
            self.set_token_strategy(token_strategy_dependency)

    @property
    def config(self):
        return self._config

    def access_token_required(self):
        """Return async callable which check if token payload has access type"""
        return self._token_required("access")

    def refresh_token_required(self):
        """Return async callable which check if token payload has refresh type"""
        return self._token_required("refresh")

    async def create_access_token(
        self,
        uid: str,
        max_age: Optional[int] = None,
        headers: Optional[Dict[str, str]] = None,
        extra: Optional[Dict[str, str]] = None,
        **kwargs,
    ):
        async def _create_access_token(
            strategy=self.TOKEN_STRATEGY, manager=self.AUTH_MANAGER
        ):
            return await manager.create_token(
                uid,
                token_type="access",
                strategy=strategy,
                max_age=max_age or self._config.JWT_ACCESS_TOKEN_MAX_AGE,
                headers=headers,
                extra_data=extra,
                **kwargs,
            )

        inject = injectable(_create_access_token)
        return await inject()

    async def create_refresh_token(
        self,
        uid: str,
        max_age: Optional[int] = None,
        headers: Optional[Dict[str, str]] = None,
        extra: Optional[Dict[str, str]] = None,
        **kwargs,
    ):
        async def _create_refresh_token(
            strategy=self.TOKEN_STRATEGY, manager=self.AUTH_MANAGER
        ):
            return await manager.create_token(
                uid,
                token_type="refresh",
                strategy=strategy,
                max_age=max_age or self._config.JWT_REFRESH_TOKEN_MAX_AGE,
                headers=headers,
                extra_data=extra,
                **kwargs,
            )

        inject = injectable(_create_refresh_token)
        return await inject()

    def user_required(
        self,
        roles: Optional[List[str]] = None,
        permissions: Optional[List[str]] = None,
        is_active: Optional[bool] = None,
        is_verified: Optional[bool] = None,
    ):
        """Return callable with current user
        if roles or permissions is set, check if user has access to this resource
        """
        sig = self._user_parser_signature()

        @with_signature(sig)
        async def _user_required(*args, **kwargs):
            token_payload = kwargs.get("token_payload")
            auth_manager: BaseAuthManager[UP, ID, RP, PP, OAP] = kwargs.get(
                "auth_manager"
            )

            user: UP = await auth_manager.get_user(
                token_payload.get("sub"), is_active, is_verified
            )
            if roles is not None or permissions is not None:
                user = await auth_manager.check_access(
                    user, roles or [], permissions or []
                )
            return user

        return _user_required

    def set_access_cookie(
        self,
        token: str,
        response: Response,
        max_age: Optional[int] = None,
        path: Optional[str] = None,
        domain: Optional[str] = None,
        secure: Optional[bool] = None,
        httponly: Optional[bool] = None,
        samesite: Optional[Literal["lax", "strict", "none"]] = None,
    ):
        """Set access cookie to response"""
        return self._set_cookie(
            response,
            token,
            self._config.COOKIE_ACCESS_TOKEN_NAME,
            max_age or self._config.COOKIE_ACCESS_TOKEN_MAX_AGE,
            path,
            domain,
            secure,
            httponly,
            samesite,
        )

    def set_refresh_cookie(
        self,
        token: str,
        response: Response,
        max_age: Optional[int] = None,
        path: Optional[str] = None,
        domain: Optional[str] = None,
        secure: Optional[bool] = None,
        httponly: Optional[bool] = None,
        samesite: Optional[Literal["lax", "strict", "none"]] = None,
    ):
        """Set refresh cookie to response"""
        return self._set_cookie(
            response,
            token,
            self._config.COOKIE_REFRESH_TOKEN_NAME,
            max_age or self._config.COOKIE_REFRESH_TOKEN_MAX_AGE,
            path,
            domain,
            secure,
            httponly,
            samesite,
        )

    def _set_cookie(
        self,
        response: Response,
        token: str,
        key: str,
        max_age: int,
        path: Optional[str] = None,
        domain: Optional[str] = None,
        secure: Optional[bool] = None,
        httponly: Optional[bool] = None,
        samesite: Optional[Literal["lax", "strict", "none"]] = None,
    ):
        response.set_cookie(
            key=key,
            value=token,
            max_age=max_age,
            expires=None,  # HTTP deprecated
            path=path or self._config.COOKIE_DEFAULT_PATH,
            domain=domain or self._config.COOKIE_DEFAULT_DOMAIN,
            secure=secure or self._config.COOKIE_DEFAULT_SECURE,
            httponly=httponly or self._config.COOKIE_DEFAULT_HTTPONLY,
            samesite=samesite or self._config.COOKIE_DEFAULT_SAMESITE,
        )
        return response

    def remove_cookies(
        self,
        response: Response,
        path: Optional[str] = None,
        domain: Optional[str] = None,
        secure: Optional[bool] = None,
        httponly: Optional[bool] = None,
        samesite: Optional[Literal["lax", "strict", "none"]] = None,
    ):
        """Remove all cookies set previously"""
        response = self._unset_cookie(
            self._config.COOKIE_ACCESS_TOKEN_NAME,
            response,
            path,
            domain,
            secure,
            httponly,
            samesite,
        )
        if self._config.ENABLE_REFRESH_TOKEN:
            response = self._unset_cookie(
                self._config.COOKIE_REFRESH_TOKEN_NAME,
                response,
                path,
                domain,
                secure,
                httponly,
                samesite,
            )
        return response

    def _unset_cookie(
        self,
        key: str,
        response: Response,
        path: Optional[str] = None,
        domain: Optional[str] = None,
        secure: Optional[bool] = None,
        httponly: Optional[bool] = None,
        samesite: Optional[Literal["lax", "strict", "none"]] = None,
    ):
        response.delete_cookie(
            key,
            path or self._config.COOKIE_DEFAULT_PATH,
            domain or self._config.COOKIE_DEFAULT_DOMAIN,
            secure or self._config.COOKIE_DEFAULT_SECURE,
            httponly or self._config.COOKIE_DEFAULT_HTTPONLY,
            samesite or self._config.COOKIE_DEFAULT_SAMESITE,
        )
        return response

    def _token_required(self, type: TokenType = "access"):
        sig = self._token_parser_signature(refresh=bool(type == "refresh"))

        @with_signature(sig)
        async def _token_type_required(*args, **kwargs):
            strategy: TokenStrategy[UP, ID] = kwargs.get("strategy")
            token: str = kwargs.get("token")

            token_payload = await strategy.read_token(token)
            if token_payload.get("type", None) != type:
                raise exceptions.TokenRequired(type)
            return token_payload

        return _token_type_required

    def _token_parser_signature(self, refresh: bool = False):
        parameters: List[Parameter] = [
            Parameter(
                name="strategy",
                kind=Parameter.POSITIONAL_OR_KEYWORD,
                default=Depends(self._get_strategy_callback()),
            ),
            Parameter(
                name="token",
                kind=Parameter.POSITIONAL_OR_KEYWORD,
                default=Depends(_get_token_from_request(self._config, refresh=refresh)),
                annotation=SecurityBase,
            ),
        ]
        return Signature(parameters)

    def _user_parser_signature(self):
        parameters: List[Parameter] = [
            Parameter(
                name="auth_manager",
                kind=Parameter.POSITIONAL_OR_KEYWORD,
                default=Depends(self._get_auth_callback()),
            ),
            Parameter(
                name="token_payload",
                kind=Parameter.POSITIONAL_OR_KEYWORD,
                default=Depends(self.access_token_required()),
            ),
        ]
        return Signature(parameters)

    @property
    def AUTH_MANAGER(self) -> BaseAuthManager:
        """Get auth service dependency"""
        return Depends(self._get_auth_callback())

    @property
    def TOKEN_STRATEGY(self) -> TokenStrategy:
        return Depends(self._get_strategy_callback())

    @property
    def ACCESS_TOKEN(self) -> Dict[str, Any]:
        return Depends(self.access_token_required())

    @property
    def REFRESH_TOKEN(self) -> Dict[str, Any]:
        return Depends(self.refresh_token_required())

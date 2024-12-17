from inspect import Parameter, Signature
from typing import Dict, Optional, List, Generic, Literal
from fastapi import Response, Depends
from fastapi.openapi.models import SecurityBase
from makefun import with_signature
from datetime import datetime, timezone, timedelta
from fastauth.manager import BaseAuthManager
from fastauth.strategy.base import TokenStrategy
from fastauth.types import TokenType
from fastauth.schema import TokenPayload
from fastauth import exceptions
from fastauth._callback import _FastAuthCallback
from fastauth.transport import _get_token_from_request
from fastauth.config import FastAuthConfig
from fastauth.utils.injector import injectable
from fastauth.models import UP, ID


class FastAuth(Generic[UP, ID], _FastAuthCallback):
    def __init__(self, config: FastAuthConfig):
        self._config = config
        super().__init__()

    @property
    def config(self):
        return self._config

    def access_token_required(self):
        """Return async callable which check if token payload has access type"""
        return self._token_required("access")

    def refresh_token_required(self):
        """Return async callable which check if token payload has refresh type"""
        return self._token_required("refresh")

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
            token_payload: TokenPayload = kwargs.get("token_payload")
            auth_manager: BaseAuthManager[UP, ID] = kwargs.get("auth_manager")

            user: UP = await auth_manager.get_user(
                token_payload.sub, is_active, is_verified
            )
            if roles is not None or permissions is not None:
                user = await auth_manager.check_access(user, roles, permissions)
            return user

        return _user_required

    async def create_access_token(
        self,
        sub: str,
        data: Optional[Dict[str, str]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs,
    ):
        """Create access token from chosen strategy"""
        injected = injectable(self._get_strategy_callback())
        strategy = await injected()
        payload = self._create_payload(sub=sub, type="access", data=data)
        return await strategy.write_token(payload, **kwargs)

    async def create_refresh_token(
        self,
        sub: str,
        data: Optional[Dict[str, str]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs,
    ) -> str:
        """Create refresh token from chosen strategy"""
        injected = injectable(self._get_strategy_callback())
        strategy = await injected()
        payload = self._create_payload(sub=sub, type="refresh", data=data)
        return await strategy.write_token(payload, **kwargs)

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

    def _create_payload(
        self,
        sub: str,
        type: TokenType,
        data: Optional[Dict[str, str]] = None,
    ):
        token_payload = TokenPayload(
            sub=sub,
            type=type,
            aud=self.config.JWT_DEFAULT_AUDIENCE,
            exp=datetime.now(timezone.utc)
            + timedelta(
                seconds=(
                    self.config.JWT_ACCESS_TOKEN_MAX_AGE
                    if type == "access"
                    else self.config.JWT_REFRESH_TOKEN_MAX_AGE
                )
            ),
            **data if data else {},
        )
        return token_payload

    def _token_required(self, type: TokenType = "access"):
        sig = self._token_parser_signature(refresh=bool(type == "refresh"))

        @with_signature(sig)
        async def _token_type_required(*args, **kwargs):
            strategy: TokenStrategy = kwargs.get("strategy")
            token: str = kwargs.get("token")
            token_payload: TokenPayload = await strategy.read_token(token)
            if token_payload.type != type:
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
    def AUTH_SERVICE(self) -> BaseAuthManager[UP, ID]:
        """Get auth service dependency"""
        return Depends(self._get_auth_callback())

    @property
    def TOKEN_STRATEGY(self) -> TokenStrategy:
        return Depends(self._get_strategy_callback())

    @property
    def ACCESS_TOKEN(self) -> TokenPayload:
        return Depends(self.access_token_required())

    @property
    def REFRESH_TOKEN(self) -> TokenPayload:
        return Depends(self.refresh_token_required())

from inspect import Parameter, Signature
from typing import Any, Callable, Coroutine, Dict, Generic, Literal

from fastapi import Depends, Response
from fastapi.openapi.models import SecurityBase
from makefun import with_signature

from fastauth import exceptions
from fastauth._callback import _FastAuthCallback
from fastauth.config import FastAuthConfig
from fastauth.manager import AuthManagerDependency, BaseAuthManager
from fastauth.models import ID, OAP, PP, RP, UP, URPP
from fastauth.strategy.base import TokenStrategy, TokenStrategyDependency
from fastauth.transport import get_token_from_request
from fastauth.types import TokenType
from fastauth.utils.injector import injectable


class FastAuth(Generic[UP, ID, RP, PP, OAP], _FastAuthCallback):
    def __init__(
        self,
        config: FastAuthConfig,
        auth_manager_dependency: (
            AuthManagerDependency[UP, ID, RP, PP, OAP] | None
        ) = None,
        token_strategy_dependency: TokenStrategyDependency[UP, ID] | None = None,
    ):
        """Main class which have security tools and dependencies

        You can set dependencies over __init__ args or use decorator:

            security = FastAuth()

            @security.set_auth_callback
            async def auth_callback(config: FastAuthConfig, **kwargs):
                return BaseAuthManager(config)


        :param config: FastAuthConfig instance
        :param auth_manager_dependency: Async callable with BaseAuthManager class implementation instance
        :param token_strategy_dependency: Async callable with TokenStrategy class implementation instance
        """

        self._config = config
        super().__init__()

        if auth_manager_dependency:
            self.set_auth_callback(auth_manager_dependency)

        if token_strategy_dependency:
            self.set_token_strategy(token_strategy_dependency)

    @property
    def config(self):
        return self._config

    def access_token_required(
        self,
    ) -> Callable[..., Coroutine[Any, Any, dict[str, Any]]]:
        """Return async callable which check if token payload has access type
        :raise TokenRequired exception raised if invalid type
        :return Async callable with decoded access token payload
        """
        return self._token_required("access")

    def refresh_token_required(
        self,
    ) -> Callable[..., Coroutine[Any, Any, dict[str, Any]]]:
        """Return async callable which check if token payload has refresh type
        :raise TokenRequired exception raised if invalid type
        :return Async callable with decoded refresh token payload
        """
        return self._token_required("refresh")

    async def create_access_token(
        self,
        uid: str,
        max_age: int | None = None,
        headers: dict[str, str] | None = None,
        extra: dict[str, str] | None = None,
        **kwargs,
    ) -> str:
        """
        Create a new access token from user model and fields defined in TokenStrategy.
        Used custom DI injector to resolve FastAPI Dependencies.
        :param uid: User ID in Database
        :param max_age: Max age, Default: FastAuthConfig.ACCESS_TOKEN_MAX_AGE
        :param headers: Optional headers for token
        :param extra: Extra data for token payload, should be dict type
        :param kwargs: Optional keyword arguments for token encoders
        :return: Token string
        """

        async def _create_access_token(
            strategy=self.TOKEN_STRATEGY, manager=self.AUTH_MANAGER
        ) -> str:
            return await manager.create_token(
                uid,
                token_type="access",
                strategy=strategy,
                max_age=max_age or self._config.ACCESS_TOKEN_MAX_AGE,
                headers=headers,
                extra_data=extra,
                **kwargs,
            )

        inject = injectable(_create_access_token)
        return await inject()

    async def create_refresh_token(
        self,
        uid: str,
        max_age: int | None = None,
        headers: dict[str, str] | None = None,
        extra: dict[str, str] | None = None,
        **kwargs,
    ) -> str:
        """
        Create a new refresh token from user model and fields defined in TokenStrategy.
        Used custom DI injector to resolve FastAPI Dependencies.
        :param uid: User ID in Database
        :param max_age: Max age, Default: FastAuthConfig.REFRESH_TOKEN_MAX_AGE
        :param headers: Optional headers for token
        :param extra: Extra data for token payload, should be dict type
        :param kwargs: Optional keyword arguments for token encoders
        :return: Token string
        """

        async def _create_refresh_token(
            strategy=self.TOKEN_STRATEGY, manager=self.AUTH_MANAGER
        ):
            return await manager.create_token(
                uid,
                token_type="refresh",
                strategy=strategy,
                max_age=max_age or self._config.REFRESH_TOKEN_MAX_AGE,
                headers=headers,
                extra_data=extra,
                **kwargs,
            )

        inject = injectable(_create_refresh_token)
        return await inject()

    def user_required(
        self,
        roles: list[str] | None = None,
        permissions: list[str] | None = None,
        is_active: bool | None = None,
        is_verified: bool | None = None,
    ) -> Callable[..., Coroutine[Any, Any, URPP | UP]]:
        """
        Return callable with current user model.
        If roles or permissions list set, checks if user has at least one role or permissions for
        provided.
        If is_active or is_verified flag set, checks if user has in this fields True or provided value

        :param roles: List of role codenames that users has to have for allowing access
        :param permissions: List of permissions codenames that users has to have
        :param is_active: Flag to check if user in DB is active
        :param is_verified: Flag to check if user in DB is verified
        :return Async callable with current user model

        """
        sig = self._user_parser_signature()

        @with_signature(sig)
        async def _user_required(**kwargs):
            token_payload = kwargs.get("token_payload")
            auth_manager: BaseAuthManager[UP, ID, RP, PP, OAP] = kwargs.get(
                "auth_manager"
            )

            user: UP = await auth_manager.get_user(
                token_payload.get("sub"), is_active, is_verified
            )

            if roles is not None or permissions is not None:
                user: URPP = await auth_manager.check_access(user, roles, permissions)
            return user

        return _user_required

    def set_access_cookie(
        self,
        token: str,
        response: Response,
        max_age: int | None = None,
        path: str | None = None,
        domain: str | None = None,
        secure: bool | None = None,
        httponly: bool | None = None,
        samesite: Literal["lax", "strict", "none"] | None = None,
    ) -> Response:
        """Set access to cookie to response
        Cookie name defined in FastAuthConfig.COOKIE_ACCESS_TOKEN_NAME
        :param token: Token string
        :param response: FastApi response
        :param max_age: Max cookie age, Default: FastAuthConfig.COOKIE_ACCESS_TOKEN_MAX_AGE
        :param path: Cookie path: Default: FastAuthConfig.COOKIE_DEFAULT_PATH
        :param domain: Cookie domain: Default: FastAuthConfig.COOKIE_DEFAULT_DOMAIN
        :param secure: Cookie secure flag: Default: FastAuthConfig.COOKIE_DEFAULT_SECURE
        :param httponly: Cookie httponly flag: Default: FastAuthConfig.COOKIE_DEFAULT_HTTPONLY
        :param samesite: Cookie samesite: Default: FastAuthConfig.COOKIE_DEFAULT_SAMESITE
        :return FastAPI Response with `set-cookie` headers
        """
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
        max_age: int | None = None,
        path: str | None = None,
        domain: str | None = None,
        secure: bool | None = None,
        httponly: bool | None = None,
        samesite: Literal["lax", "strict", "none"] | None = None,
    ) -> Response:
        """Set refresh to cookie to response
        Cookie name defined in FastAuthConfig.COOKIE_REFRESH_TOKEN_NAME
        :param token: Token string
        :param response: FastApi response
        :param max_age: Max cookie age, Default: FastAuthConfig.COOKIE_REFRESH_TOKEN_MAX_AGE
        :param path: Cookie path: Default: FastAuthConfig.COOKIE_DEFAULT_PATH
        :param domain: Cookie domain: Default: FastAuthConfig.COOKIE_DEFAULT_DOMAIN
        :param secure: Cookie secure flag: Default: FastAuthConfig.COOKIE_DEFAULT_SECURE
        :param httponly: Cookie httponly flag: Default: FastAuthConfig.COOKIE_DEFAULT_HTTPONLY
        :param samesite: Cookie samesite: Default: FastAuthConfig.COOKIE_DEFAULT_SAMESITE
        :return FastAPI Response with `set-cookie` headers"""

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
        path: str | None = None,
        domain: str | None = None,
        secure: bool | None = None,
        httponly: bool | None = None,
        samesite: Literal["lax", "strict", "none"] | None = None,
    ):
        """Set cookie to response by key and value"""
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
        path: str | None = None,
        domain: str | None = None,
        secure: bool | None = None,
        httponly: bool | None = None,
        samesite: Literal["lax", "strict", "none"] | None = None,
    ) -> Response:
        """Remove access and refresh cookie from response
        :param response: FastAPI response
        :param path: Cookie path: Default: FastAuthConfig.COOKIE_DEFAULT_PATH
        :param domain: Cookie domain: Default: FastAuthConfig.COOKIE_DEFAULT_DOMAIN
        :param secure: Cookie secure flag: Default: FastAuthConfig.COOKIE_DEFAULT_SECURE
        :param httponly: Cookie httponly flag: Default: FastAuthConfig.COOKIE_DEFAULT_HTTPONLY
        :param samesite: Cookie samesite: Default: FastAuthConfig.COOKIE_DEFAULT_SAMESITE
        :return FastAPI Response with `set-cookie=''` headers
        """
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
        path: str | None = None,
        domain: str | None = None,
        secure: bool | None = None,
        httponly: bool | None = None,
        samesite: Literal["lax", "strict", "none"] | None = None,
    ):
        """Remove cookies from response"""
        response.delete_cookie(
            key,
            path or self._config.COOKIE_DEFAULT_PATH,
            domain or self._config.COOKIE_DEFAULT_DOMAIN,
            secure or self._config.COOKIE_DEFAULT_SECURE,
            httponly or self._config.COOKIE_DEFAULT_HTTPONLY,
            samesite or self._config.COOKIE_DEFAULT_SAMESITE,
        )
        return response

    def _token_required(
        self, type: TokenType = "access"
    ) -> Callable[..., Coroutine[Any, Any, Dict[str, Any]]]:
        """Inject new signature by makefun to async callable
        and return it. User for FastAPI Dependency injection system by passing callable to depends function
        :param type: TokenType for checking required token type
        """

        sig = self._token_parser_signature(refresh=bool(type == "refresh"))

        @with_signature(sig)
        async def _token_type_required(**kwargs):
            strategy: TokenStrategy[UP, ID] = kwargs.get("strategy")
            token: str = kwargs.get("token")

            token_payload = await strategy.read_token(token)
            if token_payload.get("type", None) != type:
                raise exceptions.TokenRequired(type)
            return token_payload

        return _token_type_required

    def _token_parser_signature(self, refresh: bool = False):
        """Return signature with TokenStrategy dependency and Token string from Transport schema"""
        parameters: list[Parameter] = [
            Parameter(
                name="strategy",
                kind=Parameter.POSITIONAL_OR_KEYWORD,
                default=Depends(self._get_strategy_callback()),
            ),
            Parameter(
                name="token",
                kind=Parameter.POSITIONAL_OR_KEYWORD,
                default=Depends(get_token_from_request(self._config, refresh=refresh)),
                annotation=SecurityBase,
            ),
        ]
        return Signature(parameters)

    def _user_parser_signature(self):
        """Return signature with auth manager dependency and token payload from access_token_required callable"""
        parameters: list[Parameter] = [
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
        """Return dependency with injected auth manager callback"""
        return Depends(self._get_auth_callback())

    @property
    def TOKEN_STRATEGY(self) -> TokenStrategy:
        """Return dependency with injected token strategy callback"""
        return Depends(self._get_strategy_callback())

    @property
    def ACCESS_TOKEN(self) -> dict[str, Any]:
        """Return dependency with Access token payload"""
        return Depends(self.access_token_required())

    @property
    def REFRESH_TOKEN(self) -> dict[str, Any]:
        """Return dependency with Refresh token payload"""
        return Depends(self.refresh_token_required())

    @property
    def DEFAULT_USER(self) -> dict[str, Any]:
        """Return user_required dependency with current user which have defaults defined in config,
        where roles is FastAuthConfig.USER_DEFAULT_ROLE
        is_active is FastAuthConfig.USER_DEFAULT_IS_ACTIVE
        is_verified is FastAuthConfig.USER_DEFAULT_IS_VERIFIED
        """
        return Depends(
            self.user_required(
                roles=[self._config.USER_DEFAULT_ROLE],
                is_active=self._config.USER_DEFAULT_IS_ACTIVE,
                is_verified=self._config.USER_DEFAULT_IS_VERIFIED,
            )
        )

    @property
    def ADMIN_REQUIRED(self):
        """Return user_required dependency with admin user which have defined roles in FastAuthConfig.ADMIN_DEFAULT_ROLE
        is_active is FastAuthConfig.USER_DEFAULT_IS_ACTIVE
        is_verified is FastAuthConfig.USER_DEFAULT_IS_VERIFIED
        """
        return Depends(
            self.user_required(
                roles=[self._config.ADMIN_DEFAULT_ROLE],
                is_active=self._config.USER_DEFAULT_IS_ACTIVE,
                is_verified=self._config.USER_DEFAULT_IS_VERIFIED,
            )
        )

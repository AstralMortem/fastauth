from typing import Literal, Optional, List
from pydantic_settings import BaseSettings


class FastAuthConfig(BaseSettings):
    ENABLE_REFRESH_TOKEN: bool = True
    ENABLE_RBAC: bool = True

    ACCESS_TOKEN_LIFETIME: int = 60 * 60 * 24  # 1 day
    REFRESH_TOKEN_LIFETIME: int = 60 * 60 * 24 * 30  # 30 days

    TOKEN_LOCATION: str = "header"
    TOKEN_HEADER_NAME: str = "Authorization"
    TOKEN_HEADER_TYPE: str = "Bearer"

    JWT_SECRET: str = "secret"
    JWT_AUDIENCE: list[str] = ["fastauth:auth"]
    JWT_USER_VERIFY_AUDIENCE: list[str] = ["fastauth:verify"]
    JWT_PASSWORD_RESET_AUDIENCE: list[str] = ["fastauth:reset"]
    JWT_STATE_TOKEN_AUDIENCE: list[str] = ["fastapi-users:oauth-state"]
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_LIFETIME: int = ACCESS_TOKEN_LIFETIME
    JWT_REFRESH_TOKEN_LIFETIME: int = REFRESH_TOKEN_LIFETIME
    JWT_VERIFY_TOKEN_LIFETIME: int = 3600
    JWT_PASS_RESET_TOKEN_LIFETIME: int = 3600
    JWT_STATE_TOKEN_LIFETIME: int = 3600

    COOKIE_ACCESS_NAME: str = "fastauth_access_token"
    COOKIE_REFRESH_NAME: str = "fastauth_refresh_token"
    COOKIE_PATH: str | None = "/"
    COOKIE_DOMAIN: str | None = None
    COOKIE_SECURE: bool = False
    COOKIE_HTTPONLY: bool = False
    COOKIE_SAMESITE: Optional[Literal["lax", "strict", "none"]] = "lax"
    COOKIE_ACCESS_MAX_AGE: int = ACCESS_TOKEN_LIFETIME
    COOKIE_REFRESH_MAX_AGE: int = REFRESH_TOKEN_LIFETIME

    AUTH_ROUTER_DEFAULT_PREFIX: str = "/auth"
    TOKEN_LOGIN_URL: str = "/token/login"
    TOKEN_LOGOUT_URL: str = "/token/logout"
    TOKEN_REFRESH_URL: str = "/token/refresh"
    USERS_ROUTER_DEFAULT_PREFIX: str = "/users"
    ROLES_ROUTER_DEFAULT_PREFIX: str = "/roles"
    PERMISSION_ROUTER_DEFAULT_PREFIX: str = "/permissions"
    OAUTH_ROUTER_DEFAULT_PREFIX: str = "/oauth"

    USER_DATA_IN_REFRESH_TOKEN: bool = False
    DEFAULT_ADMIN_ROLES: List[str] = ["Admin"]
    DEFAULT_USER_ROLES: List[str] = ["User"]
    DEFAULT_USER_REGISTER_ROLE: str = "User"
    DEFAULT_CURRENT_USER_IS_ACTIVE: bool = True
    DEFAULT_CURRENT_USER_IS_VERIFIED: bool = True

    OAUTH_ASSOCIATE_WITH_EMAIL: bool = True
    OAUTH_IS_VERIFIED_DEFAULT: bool = True

from typing import Literal

from pydantic import Field, conlist
from pydantic_settings import BaseSettings

from fastauth.types import StringOrSequence, TokenLocations


class FastAuthConfig(BaseSettings):
    ACCESS_TOKEN_MAX_AGE: int = 60 * 60 * 24
    REFRESH_TOKEN_MAX_AGE: int = 60 * 60 * 24 * 20
    TOKEN_LOCATIONS: list[TokenLocations] = ["headers", "cookies"]
    ENABLE_REFRESH_TOKEN: bool = True

    # JWTHelper SECTION

    JWT_SECRET: str = ""
    JWT_ALGORITHM: str = "HS256"
    JWT_DEFAULT_AUDIENCE: StringOrSequence = ["fastauth:auth"]
    JWT_DEFAULT_VERIFICATION_AUDIENCE: StringOrSequence = ["fastauth:verification"]
    JWT_DEFAULT_RESET_AUDIENCE: StringOrSequence = ["fastauth:reset"]
    JWT_DEFAULT_STATE_AUDIENCE: StringOrSequence = ["fastauth:oauth-state"]

    JWT_ACCESS_TOKEN_MAX_AGE: int = Field(
        default_factory=lambda self: self.get("ACCESS_TOKEN_MAX_AGE")
    )
    JWT_REFRESH_TOKEN_MAX_AGE: int = Field(
        default_factory=lambda self: self.get("REFRESH_TOKEN_MAX_AGE")
    )

    JWT_VERIFY_TOKEN_MAX_AGE: int = 60 * 60
    JWT_RESET_TOKEN_MAX_AGE: int = 60 * 60
    JWT_STATE_TOKEN_MAX_AGE: int = 60 * 60

    # COOKIE SECTION

    COOKIE_ACCESS_TOKEN_NAME: str = "access_token_cookie"
    COOKIE_REFRESH_TOKEN_NAME: str = "refresh_token_cookie"
    COOKIE_ACCESS_TOKEN_MAX_AGE: int = Field(
        default_factory=lambda self: self.get("ACCESS_TOKEN_MAX_AGE")
    )
    COOKIE_REFRESH_TOKEN_MAX_AGE: int = Field(
        default_factory=lambda self: self.get("REFRESH_TOKEN_MAX_AGE")
    )
    COOKIE_DEFAULT_PATH: str = "/"
    COOKIE_DEFAULT_DOMAIN: str | None = None
    COOKIE_DEFAULT_SECURE: bool = False
    COOKIE_DEFAULT_HTTPONLY: bool = False
    COOKIE_DEFAULT_SAMESITE: Literal["lax", "strict", "none"] = "lax"

    # ROUTER SECTION

    ROUTER_AUTH_DEFAULT_PREFIX: str = "/auth"
    TOKEN_LOGIN_URL: str = "/token/login"
    TOKEN_LOGOUT_URL: str = "/token/logout"
    TOKEN_REFRESH_URL: str = "/token/refresh"

    ROUTER_USERS_DEFAULT_PREFIX: str = "/users"
    ROUTER_ROLES_DEFAULT_PREFIX: str = "/roles"
    ROUTER_PERMISSIONS_DEFAULT_PREFIX: str = "/permissions"

    # AUTH SECTION

    USER_LOGIN_FIELDS: str | conlist(str, min_length=1) = "email"
    USER_FIELDS_IN_TOKEN: conlist(str, min_length=1) = [
        "email",
        "id",
        "is_active",
        "is_verified",
    ]

    ADMIN_DEFAULT_ROLE: str = "Admin"
    USER_DEFAULT_ROLE: str = "User"
    USER_DEFAULT_IS_ACTIVE: bool | None = None
    USER_DEFAULT_IS_VERIFIED: bool | None = None

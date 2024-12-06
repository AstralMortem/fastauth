from typing import Generic
from jwt import PyJWTError
from .base import BaseStrategy
from fastauth.schemas import TokenResponse, TokenPayload
from fastauth.utils.jwt_helper import decode_jwt, encode_jwt
from fastauth import exceptions
from fastauth.models import UP
from fastauth.types import TokenType
from fastauth.config import FastAuthConfig


class JWTStrategy(Generic[UP], BaseStrategy[UP]):
    _config: FastAuthConfig

    async def read_token(self, token: str) -> TokenPayload:
        try:
            token_payload = decode_jwt(
                token,
                self._config.JWT_SECRET,
                self._config.JWT_AUDIENCE,
                [self._config.JWT_ALGORITHM],
            )
            return TokenPayload.model_validate(token_payload)
        except PyJWTError as e:
            raise exceptions.InvalidToken

    async def write_token(self, user: UP, type: TokenType = "access", **extra_fields):
        payload = TokenPayload(
            sub=str(user.id),
            aud=self._config.JWT_AUDIENCE,
            type=type,
        )

        if type == "access" or self._config.USER_DATA_IN_REFRESH_TOKEN:
            for key, val in self.set_user_fields(user).items():
                setattr(payload, key, val)

        for key, val in extra_fields.items():
            setattr(payload, key, val)

        token = encode_jwt(
            payload.model_dump(),
            secret=self._config.JWT_SECRET,
            algorithm=self._config.JWT_ALGORITHM,
            lifetime_seconds=(
                self._config.JWT_ACCESS_TOKEN_LIFETIME
                if type == "access"
                else self._config.JWT_REFRESH_TOKEN_LIFETIME
            ),
        )
        return token

    async def destroy_token(self) -> None:
        raise NotImplementedError

    def set_user_fields(self, user: UP):
        """
        Override this to set custom user fields to token
        """
        return {
            "email": user.email,
            "username": user.username if hasattr(user, "username") else None,
            "is_active": user.is_active,
            "is_verified": user.is_verified,
        }

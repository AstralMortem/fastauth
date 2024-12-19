from typing import Generic, Dict, Any
from jwt import DecodeError
from .base import TokenStrategy
from fastauth.utils.jwt_helper import JWT
from fastauth import exceptions
from fastauth.models import UP, ID
from fastauth.config import FastAuthConfig
from fastauth.types import TokenType


class JWTStrategy(Generic[UP, ID], TokenStrategy[UP, ID]):
    _config: FastAuthConfig

    def __init__(self, config: FastAuthConfig):
        super().__init__(config)
        self.encoder = JWT(config.JWT_SECRET, config.JWT_ALGORITHM)

    async def read_token(self, token: str, **kwargs) -> Dict[str, Any]:
        try:
            return self.encoder.decode_token(
                token,
                audience=kwargs.pop("aud", self._config.JWT_DEFAULT_AUDIENCE),
                **kwargs,
            )

        except DecodeError as e:
            raise exceptions.InvalidToken(f"Invalid JWT token: {e}")

    async def write_token(self, user: UP, token_type: TokenType, **kwargs) -> str:
        payload = {
            "sub": str(user.id),
            "type": token_type,
        }
        for field in self._config.USER_FIELDS_IN_TOKEN:
            if user.__dict__.get(field, False):
                payload.update({field: user.__dict__[field]})

        max_age = kwargs.pop(
            "max_age",
            (
                self._config.JWT_ACCESS_TOKEN_MAX_AGE
                if token_type == "access"
                else self._config.JWT_REFRESH_TOKEN_MAX_AGE
            ),
        )
        audience = kwargs.pop("audience", self._config.JWT_DEFAULT_AUDIENCE)
        headers = kwargs.pop("headers", None)
        if extra := kwargs.get("extra_data", {}):
            payload.update(extra)

        return self.encoder.encode_token(
            payload,
            token_type,
            max_age=max_age,
            audience=audience,
            headers=headers,
            **kwargs,
        )

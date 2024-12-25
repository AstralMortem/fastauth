from typing import Any, Generic

from jwt import DecodeError

from fastauth import exceptions
from fastauth.config import FastAuthConfig
from fastauth.models import ID, UP
from fastauth.strategy.base import TokenStrategy
from fastauth.types import TokenType
from fastauth.utils.jwt_helper import JWTHelper


class JWTStrategy(Generic[UP, ID], TokenStrategy[UP, ID]):
    _config: FastAuthConfig

    def __init__(self, config: FastAuthConfig):
        super().__init__(config)
        self.encoder = JWTHelper(config.JWT_SECRET, config.JWT_ALGORITHM)

    async def read_token(self, token: str, **kwargs) -> dict[str, Any]:
        """
        Read jwt token and return the payload
        :param token: jwt token string
        :param kwargs: Extra PyJWT decoder data(audience, leeway, issuer, etc.)
        :return: Token payload dict
        :raise InvalidToken: If the token is invalid
        """
        try:
            return self.encoder.decode_token(
                token,
                audience=kwargs.pop("audience", self._config.JWT_DEFAULT_AUDIENCE),
                **kwargs,
            )

        except DecodeError as e:
            msg = f"Invalid JWTHelper token: {e}"
            raise exceptions.InvalidToken(msg) from e

    async def write_token(self, user: UP, token_type: TokenType, **kwargs) -> str:
        """
        Write jwt token for the user model
        :param user: User model
        :param token_type: Token type (access or refresh)
        :param kwargs: extra token data(audience, max_age, headers, extra_data)
        :return: Token string
        """

        payload = {
            "sub": str(user.id),
            "type": token_type,
        }
        for field in self._config.USER_FIELDS_IN_TOKEN:
            if user.__dict__.get(field, False):
                payload.update({field: str(user.__dict__[field])})

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
        payload.update(kwargs.get("extra_data", {}))

        return self.encoder.encode_token(
            payload,
            token_type,
            max_age=max_age,
            audience=audience,
            headers=headers,
            **kwargs,
        )

from jwt import DecodeError
from .base import TokenStrategy
from fastauth.schema import TokenPayload
from fastauth.utils.jwt_helper import JWT
from fastauth import exceptions


class JWTStrategy(TokenStrategy):
    async def read_token(self, token: str, **kwargs) -> TokenPayload:
        encoder = JWT(self.config)
        try:
            token_dict = encoder.decode_token(
                token, audience=self.config.JWT_DEFAULT_AUDIENCE, **kwargs
            )
            return TokenPayload.model_validate(token_dict)
        except DecodeError as e:
            raise exceptions.InvalidToken(f"Invalid JWT token: {e}")

    async def write_token(self, payload: TokenPayload, **kwargs) -> str:
        encoder = JWT(self.config)
        try:
            dumped = payload.model_dump()
            return encoder.encode_token(
                dumped,
                (
                    self._config.JWT_ACCESS_TOKEN_MAX_AGE
                    if payload.type == "access"
                    else self._config.JWT_REFRESH_TOKEN_MAX_AGE
                ),
                audience=self.config.JWT_DEFAULT_AUDIENCE,
                **kwargs,
            )
        except Exception as e:
            raise exceptions.InvalidToken(f"Invalid token:{str(e)}")

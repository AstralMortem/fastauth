from starlette.responses import Response

from .base import BaseTransport
from fastauth.schemas import TokenPayload
from fastauth.config import FastAuthConfig


class CookieTransport(BaseTransport):

    def __init__(self, config: FastAuthConfig):
        self._config = config

    async def get_login_response(self, token: TokenPayload) -> Response:
        response = Response(status_code=204)
        response.set_cookie(
            cookie_key,
            token_string,
            cookie_max_age,
            None,
            self._config.COOKIE_PATH,
            self._config.COOKIE_DOMAIN,
            self._config.COOKIE_SECURE,
            self._config.COOKIE_HTTPONLY,
            self._config.COOKIE_SAMESITE,
        )
        return response

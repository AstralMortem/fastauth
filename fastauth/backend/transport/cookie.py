from typing import Optional
from fastapi.security import APIKeyCookie
from fastapi import Response
from .base import BaseTransport


class CookieTransport(BaseTransport):

    def schema(self):
        return APIKeyCookie(name=self._config.COOKIE_ACCESS_NAME)

    async def get_login_response(
        self, access_token: str, refresh_token: Optional[str] = None
    ) -> Response:

        response = Response(status_code=204)
        response = await self._set_cookie(
            response,
            self._config.COOKIE_ACCESS_NAME,
            access_token,
            self._config.COOKIE_ACCESS_MAX_AGE,
        )
        if self._config.ENABLE_REFRESH_TOKEN and refresh_token:
            response = await self._set_cookie(
                response,
                self._config.COOKIE_REFRESH_NAME,
                refresh_token,
                self._config.COOKIE_REFRESH_MAX_AGE,
            )

        return response

    async def get_logout_response(self) -> Response:
        response = Response(status_code=204)
        response = await self._remove_cookie(response, self._config.COOKIE_ACCESS_NAME)
        if self._config.ENABLE_REFRESH_TOKEN:
            response = await self._remove_cookie(
                response, self._config.COOKIE_REFRESH_NAME
            )
        return response

    async def _set_cookie(
        self, response: Response, name: str, token: str, max_age: int
    ):
        response.set_cookie(
            name,
            token,
            max_age,
            None,
            self._config.COOKIE_PATH,
            self._config.COOKIE_DOMAIN,
            self._config.COOKIE_SECURE,
            self._config.COOKIE_HTTPONLY,
            self._config.COOKIE_SAMESITE,
        )
        return response

    async def _remove_cookie(self, response: Response, name: str):
        response.delete_cookie(
            name,
            self._config.COOKIE_PATH,
            self._config.COOKIE_DOMAIN,
            self._config.COOKIE_SECURE,
            self._config.COOKIE_HTTPONLY,
            self._config.COOKIE_SAMESITE,
        )
        return response

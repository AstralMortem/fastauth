from typing import Optional
from fastapi.responses import JSONResponse, Response
from .base import BaseTransport
from fastauth.schemas.token import BearerTokenResponse
from fastapi.security import OAuth2PasswordBearer


class BearerTransport(BaseTransport):

    async def get_login_response(
        self, access_token: str, refresh_token: Optional[str] = None
    ) -> Response:

        payload = BearerTokenResponse(
            access_token=access_token, refresh_token=refresh_token
        )

        return JSONResponse(
            status_code=200,
            content=payload.model_dump(exclude_none=True),
        )

    async def get_logout_response(self) -> Response:
        raise NotImplementedError

    def schema(self):
        token_url = (
            self._config.AUTH_ROUTER_DEFAULT_PREFIX + self._config.TOKEN_LOGIN_URL
        )
        return OAuth2PasswordBearer(token_url)

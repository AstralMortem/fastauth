from typing import Annotated
from fastapi import APIRouter, Depends, Response
from fastapi.security import OAuth2PasswordRequestForm
from starlette.responses import JSONResponse

from fastauth.fastauth import FastAuth
from fastauth.schema import TokenResponse
from fastauth.transport import TRANSPORT_GETTER


def get_auth_router(security: FastAuth):
    config = security.config
    router = APIRouter(prefix=config.ROUTER_AUTH_DEFAULT_PREFIX)

    @router.post(config.TOKEN_LOGIN_URL)
    async def login(
        credentials: Annotated[OAuth2PasswordRequestForm, Depends()],
        auth_service=security.AUTH_SERVICE,
    ):
        user = await auth_service.authenticate(
            credentials.username, credentials.password
        )
        user_data = {}
        for field in config.USER_FIELDS_IN_TOKEN:
            if user.__dict__.get(field, False):
                user_data.update({field: user.__dict__[field]})

        token_content = TokenResponse(
            access_token=await security.create_access_token(
                str(user.id), data=user_data
            ),
            refresh_token=(
                await security.create_refresh_token(str(user.id))
                if config.ENABLE_REFRESH_TOKEN
                else None
            ),
        )
        response = JSONResponse(None, status_code=200)

        for location in config.TOKEN_LOCATIONS:
            transport_cls = TRANSPORT_GETTER[location]
            transport = transport_cls(config)
            response = await transport.login_response(
                security,
                token_content,
                response,
            )

        return response

    @router.post(config.TOKEN_LOGOUT_URL, dependencies=[security.ACCESS_TOKEN])
    async def logout():
        response = Response(None, status_code=204)

        for location in config.TOKEN_LOCATIONS:
            transport_cls = TRANSPORT_GETTER[location]
            transport = transport_cls(config)
            response = await transport.logout_response(
                security,
                response,
            )

        return response

    if config.ENABLE_REFRESH_TOKEN:

        @router.post(config.TOKEN_REFRESH_URL)
        async def refresh(
            token=security.REFRESH_TOKEN,
            auth_service=security.AUTH_SERVICE,
        ):
            uid = token.sub
            user = await auth_service.get_user(uid)

            user_data = {}
            for field in config.USER_FIELDS_IN_TOKEN:
                if user.__dict__.get(field, False):
                    user_data.update({field: user.__dict__[field]})

            token_content = TokenResponse(
                access_token=await security.create_access_token(uid, data=user_data),
                refresh_token=(await security.create_refresh_token(uid)),
            )

            response = JSONResponse(None, status_code=200)

            for location in config.TOKEN_LOCATIONS:
                transport_cls = TRANSPORT_GETTER[location]
                transport = transport_cls(config)
                response = await transport.login_response(
                    security,
                    token_content,
                    response,
                )

            return response

    return router

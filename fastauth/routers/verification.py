from fastapi import APIRouter, Request

from fastauth import FastAuth
from fastauth.schema import UR_S


def get_verify_router(security: FastAuth, user_read: type[UR_S]):
    router = APIRouter(prefix=security.config.ROUTER_AUTH_DEFAULT_PREFIX)

    @router.post("/request-verify-token/{email}")
    async def request_verify_token(
        request: Request, email: str, manager=security.AUTH_MANAGER
    ):
        await manager.request_verify(email, request)

    @router.post("/verify/{token}", response_model=user_read)
    async def verify_token(request: Request, token: str, manager=security.AUTH_MANAGER):
        return await manager.verify(token, request)

    return router

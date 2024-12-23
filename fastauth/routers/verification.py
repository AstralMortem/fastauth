from fastapi import APIRouter

from fastauth import FastAuth
from fastauth.schema import UR_S


def get_verify_router(security: FastAuth, user_read: type[UR_S]):
    router = APIRouter(prefix=security.config.ROUTER_AUTH_DEFAULT_PREFIX)

    @router.post("/request-verify-token/{email}")
    async def request_verify_token(email: str, manager=security.AUTH_MANAGER):
        # TODO: remove return
        return await manager.request_verify(email)

    @router.post("/verify/{token}", response_model=user_read)
    async def verify_token(token: str, manager=security.AUTH_MANAGER):
        return await manager.verify(token)

    return router

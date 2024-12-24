from fastapi import APIRouter, Request

from fastauth.fastauth import FastAuth
from fastauth.schema import UC_S, UR_S


def get_register_router(
    security: FastAuth, user_read: type[UR_S], user_create: type[UC_S]
):
    router = APIRouter(prefix=security.config.ROUTER_AUTH_DEFAULT_PREFIX)

    @router.post("/register", response_model=user_read)
    async def register(
        request: Request, data: user_create, auth_manager=security.AUTH_MANAGER
    ):
        return await auth_manager.register(data, request=request)

    return router

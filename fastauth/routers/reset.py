from fastapi import APIRouter, Body, Request

from fastauth import FastAuth


def get_reset_password_router(security: FastAuth):
    router = APIRouter(prefix=security.config.ROUTER_AUTH_DEFAULT_PREFIX)

    @router.post("/forgot-password/{email}")
    async def forgot_password(
        request: Request, email: str, manager=security.AUTH_MANAGER
    ):
        await manager.forgot_password(email, request)

    @router.post("/reset-password")
    async def reset_password(
        request: Request,
        token: str = Body(),
        new_password: str = Body(),
        manager=security.AUTH_MANAGER,
    ):
        await manager.reset_password(token, new_password, request)

    return router

from fastapi import APIRouter, Body

from fastauth import FastAuth


def get_reset_password_router(security: FastAuth):
    router = APIRouter(prefix=security.config.ROUTER_AUTH_DEFAULT_PREFIX)

    @router.post("/forgot-password/{email}")
    async def forgot_password(email: str, manager=security.AUTH_MANAGER):
        return await manager.forgot_password(email)

    @router.post("/reset-password")
    async def reset_password(
        token: str = Body(), new_password: str = Body(), manager=security.AUTH_MANAGER
    ):
        return await manager.reset_password(token, new_password)

    return router

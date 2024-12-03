from fastapi import APIRouter, Body, Response
from pydantic import EmailStr

from fastauth.fastauth import FastAuth


def get_password_router(self: FastAuth):
    router = APIRouter(prefix=self.config.AUTH_ROUTER_DEFAULT_PREFIX)

    @router.post("/forgot-password")
    async def forgot_password(
        email: EmailStr = Body(..., embed=True), manager=self.AUTH_MANAGER
    ):
        await manager.forgot_password(email)
        return Response(status_code=204)

    @router.post("/reset-password")
    async def reset_password(
        token: str = Body(..., embed=True),
        password: str = Body(..., embed=True),
        manager=self.AUTH_MANAGER,
    ):
        await manager.reset_password(token, password)
        return Response(status_code=204)

    return router

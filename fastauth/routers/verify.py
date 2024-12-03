from typing import Type
from fastapi import APIRouter, Body, Response, status
from pydantic import EmailStr

from fastauth.fastauth import FastAuth
from fastauth.schemas import UR_DTO


def get_verify_router(self: FastAuth, user_read: Type[UR_DTO]):
    router = APIRouter(prefix=self.config.AUTH_ROUTER_DEFAULT_PREFIX)

    @router.post("/request-verify")
    async def request_verify_token(
        email: EmailStr = Body(..., embed=True), manager=self.AUTH_MANAGER
    ):
        await manager.request_verify(email)
        return Response(status_code=204)

    @router.post("/verify", response_model=user_read)
    async def verify_user(
        token: str = Body(..., embed=True), manager=self.AUTH_MANAGER
    ):
        user = await manager.verify(token)
        return user

    return router

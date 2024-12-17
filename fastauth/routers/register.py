from fastapi import APIRouter
from typing import Type
from fastauth.fastauth import FastAuth
from fastauth.schema import UR_S, UC_S


def get_register_router(
    security: FastAuth, user_read: Type[UR_S], user_create: Type[UC_S]
):
    router = APIRouter()

    @router.post("/register", response_model=user_read)
    async def register(data: user_create, auth_manager=security.AUTH_SERVICE):
        return await auth_manager.register(data)

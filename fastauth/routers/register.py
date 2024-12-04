from typing import Type, Optional
from fastapi import APIRouter
from fastauth.fastauth import FastAuth
from fastauth.schemas import UR_DTO, UC_DTO


def get_register_router(
    self: FastAuth,
    user_read: Type[UR_DTO],
    user_create: Type[UC_DTO],
    default_role: Optional[str] = None,
):
    router = APIRouter(prefix=self.config.AUTH_ROUTER_DEFAULT_PREFIX)

    @router.post("/register", response_model=user_read)
    async def register(data: user_create, manager=self.AUTH_MANAGER):
        return await manager.create_user(data, default_role=default_role)

    return router

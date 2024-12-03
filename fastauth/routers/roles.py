from fastapi import APIRouter

from fastauth.fastauth import FastAuth
from fastauth.schemas import RU_DTO, RC_DTO, RR_DTO, PR_DTO, PU_DTO, PC_DTO
from typing import Type


def get_roles_router(
    self: FastAuth,
    role_read: Type[RR_DTO],
    role_create: Type[RR_DTO],
    role_update: Type[RU_DTO],
):
    router = APIRouter(prefix=self.config.ROLES_ROUTER_DEFAULT_PREFIX)

    @router.get("/{id}", dependencies=[self.ADMIN_REQUIRED], response_model=role_read)
    async def get_role(id: int, manager=self.AUTH_MANAGER):
        return await manager.get_role(id)

    @router.post("/", dependencies=[self.ADMIN_REQUIRED], response_model=role_read)
    async def create_role(data: role_create, manager=self.AUTH_MANAGER):
        return await manager.create_role(data)

    return router

from fastapi import APIRouter, Depends
from fastauth.fastauth import FastAuth
from fastauth.schemas import RU_DTO, RC_DTO, RR_DTO
from typing import Type, Optional, List


def get_roles_router(
    self: FastAuth,
    role_read: Type[RR_DTO],
    role_create: Type[RC_DTO],
    role_update: Type[RU_DTO],
    default_roles: Optional[List[str]] = None,
    default_permissions: Optional[List[str]] = None,
):
    router = APIRouter(prefix=self.config.ROLES_ROUTER_DEFAULT_PREFIX)
    secured = self.ADMIN_REQUIRED
    if default_roles or default_permissions:
        secured = Depends(
            self.current_user(roles=default_roles, permissions=default_permissions)
        )

    @router.get("/{id}", dependencies=[secured], response_model=role_read)
    async def get_role(id: int, manager=self.AUTH_MANAGER):
        return await manager.get_role(id)

    @router.post("/", dependencies=[secured], response_model=role_read)
    async def create_role(data: role_create, manager=self.AUTH_MANAGER):
        return await manager.create_role(data)

    @router.patch("/{id}", dependencies=[secured], response_model=role_read)
    async def update_role(id: int, data: role_update, manager=self.AUTH_MANAGER):
        return await manager.update_role(id, data)

    @router.delete("/{id}", dependencies=[secured])
    async def delete_role(id: int, manager=self.AUTH_MANAGER):
        await manager.delete_role(id)

    return router

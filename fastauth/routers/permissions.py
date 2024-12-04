from fastapi import APIRouter, Depends
from fastauth.fastauth import FastAuth
from fastauth.schemas import PC_DTO, PU_DTO, PR_DTO
from typing import Type, Optional, List


def get_permissions_router(
    self: FastAuth,
    permission_read: Type[PR_DTO],
    permission_create: Type[PC_DTO],
    permission_update: Type[PU_DTO],
    default_roles: Optional[List[str]] = None,
    default_permissions: Optional[List[str]] = None,
):
    router = APIRouter(prefix=self.config.PERMISSION_ROUTER_DEFAULT_PREFIX)
    secured = self.ADMIN_REQUIRED
    if default_roles or default_permissions:
        secured = Depends(
            self.current_user(
                roles=default_permissions, permissions=default_permissions
            )
        )

    @router.get("/{id}", dependencies=[secured], response_model=permission_read)
    async def get_permission(id: int, manager=self.AUTH_MANAGER):
        return await manager.get_permission(id)

    @router.post("/", dependencies=[secured], response_model=permission_read)
    async def create_permission(data: permission_create, manager=self.AUTH_MANAGER):
        return await manager.create_permission(data)

    @router.patch("/{id}", dependencies=[secured], response_model=permission_read)
    async def update_permission(
        id: int, data: permission_update, manager=self.AUTH_MANAGER
    ):
        return await manager.update_permission(id, data)

    @router.delete("/{id}", dependencies=[secured])
    async def delete_permission(id: int, manager=self.AUTH_MANAGER):
        await manager.delete_permission(id)

    return router

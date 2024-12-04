from fastapi import APIRouter

from fastauth.fastauth import FastAuth
from fastauth.schemas import UR_DTO, UC_DTO, UU_DTO
from typing import Type, Optional


def get_users_router(
    self: FastAuth,
    user_read: Type[UR_DTO],
    user_create: Type[UC_DTO],
    user_update: Type[UU_DTO],
    default_role: Optional[str] = None,
):
    router = APIRouter(prefix=self.config.USERS_ROUTER_DEFAULT_PREFIX)

    @router.get("/me", response_model=user_read)
    async def get_me(user=self.USER_REQUIRED):
        return user

    @router.patch("/me", response_model=user_read)
    async def update_me(
        data: user_update,
        manager=self.AUTH_MANAGER,
        user=self.USER_REQUIRED,
    ):
        user_id = manager.parse_user_id(user.id)
        return await manager.update_user(user_id, data)

    @router.patch(
        "/{id}",
        response_model=user_read,
        dependencies=[self.ADMIN_REQUIRED],
    )
    async def update_user(id: str, data: user_update, manager=self.AUTH_MANAGER):
        user_id = manager.parse_user_id(id)
        return await manager.update_user(user_id, data)

    @router.delete(
        "/{id}",
        dependencies=[self.ADMIN_REQUIRED],
    )
    async def delete_user(id: str, manager=self.AUTH_MANAGER):
        user_id = manager.parse_user_id(id)
        return await manager.delete_user(user_id)

    @router.get(
        "/{id}",
        dependencies=[self.ADMIN_REQUIRED],
    )
    async def get_user(id: str, manager=self.AUTH_MANAGER):
        user_id = manager.parse_user_id(id)
        return await manager.get_user(user_id)

    @router.post(
        "/",
        dependencies=[self.ADMIN_REQUIRED],
    )
    async def create_user(data: user_create, manager=self.AUTH_MANAGER):
        return await manager.create_user(data, False, default_role=default_role)

    return router

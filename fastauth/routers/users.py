from typing import Type

from fastapi import APIRouter

from fastauth.fastauth import FastAuth
from fastauth.schema import UR_S, UU_S


def get_users_router(
    security: FastAuth,
    user_read: Type[UR_S],
    user_update: Type[UU_S],
    is_active: bool | None = None,
    is_verified: bool | None = None,
):

    router = APIRouter(prefix=security.config.ROUTER_USERS_DEFAULT_PREFIX)

    @router.get("/me", response_model=user_read)
    async def get_me(
        user=security.user_required(is_active=is_active, is_verified=is_verified)
    ):
        return user

    @router.patch("/me", response_model=user_read)
    async def patch_me(
        data: user_update, user=security.user_required(), manager=security.AUTH_MANAGER
    ):
        return await manager._update_user(user, data.model_dump(exclude_unset=True))

    @router.get("/{id}", response_model=user_read)
    async def get_user(id: str, manager=security.AUTH_MANAGER):
        return await manager.get_user(id, is_active, is_verified)

    @router.patch("/{id}", response_model=user_read)
    async def update_user(id: str, data: user_update, manager=security.AUTH_MANAGER):
        return await manager.patch_user(id, data)

    @router.delete("/{id}", response_model=user_read)
    async def delete_user(id: str, manager=security.AUTH_MANAGER):
        return await manager.delete_user(id)

    return router

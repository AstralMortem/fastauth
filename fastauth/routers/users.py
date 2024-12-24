from fastapi import APIRouter, Depends, Request

from fastauth.fastauth import FastAuth
from fastauth.schema import UR_S, UU_S


def get_users_router(
    security: FastAuth,
    user_read: type[UR_S],
    user_update: type[UU_S],
    is_active: bool | None = None,
    is_verified: bool | None = None,
):
    router = APIRouter(prefix=security.config.ROUTER_USERS_DEFAULT_PREFIX)

    @router.get("/me", response_model=user_read)
    async def get_me(
        user=Depends(
            security.user_required(is_active=is_active, is_verified=is_verified)
        ),
    ):
        return user

    @router.patch("/me", response_model=user_read)
    async def patch_me(
        request: Request,
        data: user_update,
        user=Depends(
            security.user_required(is_active=is_active, is_verified=is_verified)
        ),
        manager=security.AUTH_MANAGER,
    ):
        return await manager._update_user(
            user, data.model_dump(exclude_unset=True), request
        )

    @router.get("/{id}", response_model=user_read)
    async def get_user(id: str, manager=security.AUTH_MANAGER):
        return await manager.get_user(id, is_active, is_verified)

    @router.patch("/{id}", response_model=user_read)
    async def update_user(
        request: Request, id: str, data: user_update, manager=security.AUTH_MANAGER
    ):
        return await manager.patch_user(id, data, request)

    @router.delete("/{id}", response_model=user_read)
    async def delete_user(request: Request, id: str, manager=security.AUTH_MANAGER):
        return await manager.delete_user(id, request)

    return router

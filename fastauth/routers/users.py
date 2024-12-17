from typing import Type

from fastapi import APIRouter

from fastauth.fastauth import FastAuth
from fastauth.schema import UC_S, UR_S, UU_S


def get_users_router(
    security: FastAuth,
    user_read: Type[UR_S],
    user_create: Type[UC_S],
    user_update: Type[UU_S],
):

    router = APIRouter(prefix=security.config.ROUTER_USERS_DEFAULT_PREFIX)

    @router.get("/me", response_model=user_read)
    async def get_me(user=security.user_required()):
        return user

    @router.patch("/me", response_model=user_read)
    async def patch_me(
        data: user_update, user=security.user_required(), manager=security.AUTH_SERVICE
    ):
        return await manager.user_repo.update(user, data.model_dump(exclude_unset=True))

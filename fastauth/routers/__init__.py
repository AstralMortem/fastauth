from fastapi import APIRouter

from fastauth.fastauth import FastAuth
from fastauth.routers.auth import get_auth_router
from fastauth.routers.register import get_register_router
from fastauth.routers.users import get_users_router
from fastauth.schema import UC_S, UR_S, UU_S


class FastAuthRouter:
    def __init__(self, security: FastAuth):
        self.security = security

    def get_auth_router(self) -> APIRouter:
        return get_auth_router(self.security)

    def get_register_router(
        self, user_read: type[UR_S], user_create: type[UC_S]
    ) -> APIRouter:
        return get_register_router(self.security, user_read, user_create)

    def get_users_router(
        self,
        user_read: type[UR_S],
        user_update: type[UU_S],
        is_active: bool | None = None,
        is_verified: bool | None = None,
    ):
        return get_users_router(
            self.security, user_read, user_update, is_active, is_verified
        )

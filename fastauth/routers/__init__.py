from typing import Type

from fastapi import APIRouter

from fastauth.fastauth import FastAuth
from .auth import get_auth_router
from .register import get_register_router
from fastauth.schema import UR_S, UC_S, UU_S
from .users import get_users_router


class FastAuthRouter:
    def __init__(self, security: FastAuth):
        self.security = security

    def get_auth_router(self) -> APIRouter:
        return get_auth_router(self.security)

    def get_register_router(
        self, user_read: Type[UR_S], user_create: Type[UC_S]
    ) -> APIRouter:
        return get_register_router(self.security, user_read, user_create)

    def get_users_router(
        self,
        user_read: Type[UR_S],
        user_update: Type[UU_S],
        is_active: bool | None = None,
        is_verified: bool | None = None,
    ):
        return get_users_router(
            self.security, user_read, user_update, is_active, is_verified
        )

from typing import Type

from fastapi import FastAPI

from fastauth.schemas import UR_DTO, UC_DTO, UU_DTO
from fastauth.fastauth import FastAuth
from .auth import get_auth_router
from .password import get_password_router
from .register import get_register_router
from .users import get_users_router
from .verify import get_verify_router


class FastAuthRouter:
    def __init__(self, security: FastAuth):
        self._security = security

    def get_auth_router(self):
        return get_auth_router(self._security)

    def get_users_router(
        self,
        user_read: Type[UR_DTO],
        user_create: Type[UC_DTO],
        user_update: Type[UU_DTO],
    ):
        return get_users_router(self._security, user_read, user_create, user_update)

    def get_register_router(self, user_read: Type[UR_DTO], user_create: Type[UC_DTO]):
        return get_register_router(self._security, user_read, user_create)

    def get_verify_router(self, user_read: Type[UR_DTO]):
        return get_verify_router(self._security, user_read)

    def get_password_router(self):
        return get_password_router(self._security)

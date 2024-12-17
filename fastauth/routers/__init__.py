from typing import Type

from fastapi import APIRouter

from fastauth.fastauth import FastAuth
from .auth import get_auth_router
from .register import get_register_router
from fastauth.schema import UR_S, UC_S


class FastAuthRouter:
    def __init__(self, security: FastAuth):
        self.security = security

    def get_auth_router(self) -> APIRouter:
        return get_auth_router(self.security)

    def get_register_router(
        self, user_read: Type[UR_S], user_create: Type[UC_S]
    ) -> APIRouter:
        return get_register_router(self.security, user_read, user_create)

from timeit import default_timer
from typing import Type, Optional, List, Union, Tuple, Dict, Any

from fastapi import FastAPI, APIRouter
from httpx_oauth.oauth2 import BaseOAuth2
from fastauth.schemas import (
    UR_DTO,
    UC_DTO,
    UU_DTO,
    RR_DTO,
    RC_DTO,
    RU_DTO,
    PU_DTO,
    PC_DTO,
)
from fastauth.fastauth import FastAuth
from .auth import get_auth_router
from .oauth import get_oauth_router
from .password import get_password_router
from .permissions import get_permissions_router
from .register import get_register_router
from .roles import get_roles_router
from .users import get_users_router
from .verify import get_verify_router
from ..schemas.base import DTO


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

    def get_register_router(
        self,
        user_read: Type[UR_DTO],
        user_create: Type[UC_DTO],
        default_role: Optional[str] = None,
    ):
        return get_register_router(
            self._security, user_read, user_create, default_role=default_role
        )

    def get_verify_router(self, user_read: Type[UR_DTO]):
        return get_verify_router(self._security, user_read)

    def get_password_router(self):
        return get_password_router(self._security)

    def get_roles_router(
        self,
        role_read: Type[RR_DTO],
        role_create: Type[RC_DTO],
        role_update: Type[RU_DTO],
        default_roles: Optional[List[str]] = None,
        default_permissions: Optional[List[str]] = None,
    ):
        return get_roles_router(
            self._security,
            role_read,
            role_create,
            role_update,
            default_roles,
            default_permissions,
        )

    def get_permission_router(
        self,
        permission_read: Type[PU_DTO],
        permission_create: Type[PC_DTO],
        permission_update: Type[PU_DTO],
        default_roles: Optional[List[str]] = None,
        default_permissions: Optional[List[str]] = None,
    ):
        return get_permissions_router(
            self._security,
            permission_read,
            permission_create,
            permission_update,
            default_roles,
            default_permissions,
        )

    def get_oauth_router(
        self,
        oauth_client: BaseOAuth2,
        redirect_url: Optional[str] = None,
        default_role: Optional[str] = None,
    ):
        return get_oauth_router(
            self._security, oauth_client, redirect_url, default_role
        )

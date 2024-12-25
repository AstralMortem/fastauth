from fastapi import APIRouter, FastAPI
from httpx_oauth.oauth2 import BaseOAuth2

from fastauth.fastauth import FastAuth
from fastauth.routers.auth import get_auth_router
from fastauth.routers.oauth import get_oauth_router
from fastauth.routers.rbac import get_permissions_router, get_roles_router
from fastauth.routers.register import get_register_router
from fastauth.routers.reset import get_reset_password_router
from fastauth.routers.users import get_users_router
from fastauth.routers.verification import get_verify_router
from fastauth.schema import PC_S, PR_S, PU_S, RC_S, RR_S, RU_S, UC_S, UR_S, UU_S
from fastauth.schema.base import BaseSchema


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

    def get_roles_router(
        self,
        role_read: type[RR_S],
        role_create: type[RC_S],
        role_update: type[RU_S],
        default_admin_role: str | None = None,
        is_active: bool | None = None,
        is_verified: bool | None = None,
    ):
        return get_roles_router(
            self.security,
            role_read,
            role_create,
            role_update,
            default_admin_role,
            is_active,
            is_verified,
        )

    def get_permissions_router(
        self,
        permission_read: type[PR_S],
        permission_create: type[PC_S],
        permission_update: type[PU_S],
        default_admin_role: str | None = None,
        is_active: bool | None = None,
        is_verified: bool | None = None,
    ):
        return get_permissions_router(
            self.security,
            permission_read,
            permission_create,
            permission_update,
            default_admin_role,
            is_active,
            is_verified,
        )

    def get_verify_router(self, user_read: type[UR_S]):
        return get_verify_router(self.security, user_read)

    def get_reset_router(self):
        return get_reset_password_router(self.security)

    def get_oauth_router(
        self,
        client: BaseOAuth2,
        redirect_url: str | None = None,
        default_role: str | bool | None = None,
    ):
        return get_oauth_router(self.security, client, redirect_url, default_role)

    def register_in_fastapi(
        self, app: FastAPI, schema_map: dict[str, dict[str, type[BaseSchema]]]
    ):
        user_schema = schema_map.get("user")
        role_schema = schema_map.get("role", None)
        permission_schema = schema_map.get("permission", None)

        routers = [
            (self.get_auth_router(), {"tags": ["Auth"]}),
            (
                self.get_register_router(
                    user_schema.get("read"), user_schema.get("create")
                ),
                {"tags": ["Auth"]},
            ),
            (
                self.get_users_router(
                    user_schema.get("read"),
                    user_schema.get("update"),
                    user_schema.get("is_active", None),
                    user_schema.get("is_verified", None),
                ),
                {"tags": ["Users"]},
            ),
            (self.get_reset_router(), {"tags": ["Auth"]}),
            (self.get_verify_router(user_schema.get("read")), {"tags": ["Auth"]}),
            (
                (
                    self.get_roles_router(
                        role_schema.get("read"),
                        role_schema.get("create"),
                        role_schema.get("update"),
                        role_schema.get("default_admin_role", None),
                        user_schema.get("is_active", None),
                        user_schema.get("is_verified"),
                    ),
                    {"tags": ["Roles"]},
                )
                if role_schema
                else None
            ),
            (
                (
                    self.get_permissions_router(
                        permission_schema.get("read"),
                        permission_schema.get("create"),
                        permission_schema.get("read"),
                        role_schema.get("default_admin_role", None),
                        user_schema.get("is_active", None),
                        user_schema.get("is_verified"),
                    ),
                    {"tags": ["Permission"]},
                )
                if permission_schema
                else None
            ),
        ]

        for router, kwargs in routers:
            app.include_router(router, **kwargs)

        return app

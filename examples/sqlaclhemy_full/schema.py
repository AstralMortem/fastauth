import uuid

from fastauth.schema import (
    BaseOAuthRead,
    BasePermissionCreate,
    BasePermissionRead,
    BasePermissionUpdate,
    BaseRoleCreate,
    BaseRoleRead,
    BaseUserCreate,
    BaseUserRead,
    BaseUserUpdate,
    OAuthMixin,
    RBACMixin,
)


class PermissionRead(BasePermissionRead):
    pass


class PermissionCreate(BasePermissionCreate):
    pass


class PermissionUpdate(BasePermissionUpdate):
    pass


class RoleRead(BaseRoleRead[PermissionRead]):
    pass


class RoleCreate(BaseRoleCreate):
    pass


class RoleUpdate(BaseUserUpdate):
    pass


class OAuthRead(BaseOAuthRead[uuid.UUID]):
    pass


class UserRead(
    BaseUserRead[uuid.UUID], RBACMixin[RoleRead, PermissionRead], OAuthMixin[OAuthRead]
):
    pass


class UserCreate(BaseUserCreate, RBACMixin[RoleRead, PermissionRead]):
    pass


class UserUpdate(BaseUserUpdate):
    pass


ROUTER_SCHEMA = {
    "user": {
        "read": UserRead,
        "create": UserCreate,
        "update": UserUpdate,
        "is_active": True,
        "is_verified": False,
    },
    "role": {
        "read": RoleRead,
        "create": RoleCreate,
        "update": RoleUpdate,
    },
    "permission": {
        "read": PermissionRead,
        "create": PermissionCreate,
        "update": PermissionUpdate,
    },
}

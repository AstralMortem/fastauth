import uuid
from fastauth.schema import (
    BasePermissionRead,
    BasePermissionCreate,
    BasePermissionUpdate,
    BaseRoleRead,
    BaseRoleUpdate,
    BaseRoleCreate,
    BaseUserRead,
    RBACMixin,
    OAuthMixin,
    BaseUserCreate,
    BaseUserUpdate,
    BaseOAuthRead,
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


class RoleUpdate(BaseRoleUpdate):
    pass


class OAuthRead(BaseOAuthRead):
    pass


class UserRead(
    BaseUserRead[uuid.UUID], RBACMixin[RoleRead, PermissionRead], OAuthMixin[OAuthRead]
):
    pass


class UserCreate(BaseUserCreate, RBACMixin):
    pass


class UserUpdate(BaseUserUpdate):
    pass

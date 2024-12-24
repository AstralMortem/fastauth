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
    BaseUserCreate,
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


class UserRead(BaseUserRead[uuid.UUID], RBACMixin[RoleRead, PermissionRead]):
    pass


class UserCreate(BaseUserCreate, RBACMixin):
    pass

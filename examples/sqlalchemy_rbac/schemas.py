import uuid

from fastauth.schemas import (
    BaseRoleRead,
    BaseRoleCreate,
    BaseRoleUpdate,
    BasePermissionRead,
    BasePermissionCreate,
    BasePermissionUpdate,
    BaseUserCreate,
    BaseUserUpdate,
    BaseUserRead,
    BaseRBACMixin,
    BaseRBACCreateMixin,
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


class UserRead(BaseUserRead[uuid.UUID], BaseRBACMixin[RoleRead]):
    pass


class UserCreate(BaseUserCreate, BaseRBACCreateMixin):
    pass


class UserUpdate(BaseUserUpdate):
    pass

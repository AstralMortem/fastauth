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
    UserRBACMixin,
)


class UserRead(BaseUserRead[uuid.UUID], UserRBACMixin):
    pass


class UserCreate(BaseUserCreate):
    pass


class UserUpdate(BaseUserUpdate):
    pass


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

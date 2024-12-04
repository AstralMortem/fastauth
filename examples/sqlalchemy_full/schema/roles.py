from fastauth.schemas import BaseRoleRead, BaseRoleUpdate, BaseRoleCreate
from .permission import PermissionRead


class RoleRead(BaseRoleRead[PermissionRead]):
    pass


class RoleUpdate(BaseRoleUpdate):
    pass


class RoleCreate(BaseRoleCreate):
    pass

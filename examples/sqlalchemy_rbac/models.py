import uuid
from examples.db import Model
from fastauth.contrib.sqlalchemy import models


class User(models.SQLAlchemyUserUUID, models.SQLAlchemyRBACMixin, Model):
    pass


class Role(models.SQLAlchemyRole[int], Model):
    pass


class Permission(models.SQLAlchemyPermission[int], Model):
    pass


class RolePermission(models.SQLAlchemyRolePermissionRel[int, int], Model):
    pass


class UserRole(models.SQLAlchemyUserRoleRel[uuid.UUID, int], Model):
    pass


class UserPermission(models.SQLAlchemyUserPermissionRel[uuid.UUID, int], Model):
    pass

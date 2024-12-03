import uuid
from examples.db import Model
from fastauth.contrib.sqlalchemy import models


class User(models.SQLAlchemyUserUUID, models.SQLAlchemyRBACMixin, Model):
    pass


class Role(models.SQLAlchemyRole, Model):
    pass


class Permission(models.SQLAlchemyPermission, Model):
    pass


class RolePermission(models.SQLAlchemyRolePermissionRel, Model):
    pass


class UserRole(models.SQLAlchemyUserRoleRel[uuid.UUID], Model):
    pass


class UserPermission(models.SQLAlchemyUserPermissionRel[uuid.UUID], Model):
    pass

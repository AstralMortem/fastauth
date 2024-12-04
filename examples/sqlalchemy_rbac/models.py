from typing import List

from sqlalchemy.orm import Mapped, relationship

from examples.db import Model
from fastauth.contrib.sqlalchemy import models


class User(models.SQLAlchemyUserUUID, models.SQLAlchemyRBACMixin, Model):
    role: Mapped["Role"] = relationship(lazy="joined")


class Role(models.SQLAlchemyRole, Model):
    permissions: Mapped[List["Permission"]] = relationship(
        secondary="role_permission_rel", lazy="joined"
    )


class Permission(models.SQLAlchemyPermission, Model):
    pass


class RolePermission(models.SQLAlchemyRolePermissionRel, Model):
    pass

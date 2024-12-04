from typing import List
from sqlalchemy.orm import Mapped, relationship
from fastauth.contrib.sqlalchemy import models
from examples.db import Model


class User(models.SQLAlchemyUserUUID, models.SQLAlchemyRBACMixin, Model):
    role: Mapped["Role"] = relationship(lazy="joined")
    oauth_accounts: Mapped[List["OAuthAccount"]] = relationship(lazy="joined")


class Role(models.SQLAlchemyRole, Model):
    permissions: Mapped[List["Permission"]] = relationship(
        secondary="role_permission_rel", lazy="joined"
    )


class Permission(models.SQLAlchemyPermission, Model):
    pass


class OAuthAccount(models.SQLAlchemyOAuthAccountUUID, Model):
    pass


class RolePermission(models.SQLAlchemyRolePermissionRel, Model):
    pass

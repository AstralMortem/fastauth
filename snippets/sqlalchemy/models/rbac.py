from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from fastauth.contrib.sqlalchemy import models


class Model(DeclarativeBase):
    pass


class Role(models.SQLAlchemyBaseRole, Model):
    permissions: Mapped[list["Permission"]] = relationship(
        secondary="role_permission_rel", lazy="joined"
    )


class Permission(models.SQLAlchemyBasePermission, Model):
    pass


class RolePermissionRel(models.SQLAlchemyBaseRolePermissionRel, Model):
    pass


class User(models.SQLAlchemyBaseUserUUID, models.UserRBACMixin, Model):
    role: Mapped[Role] = relationship(lazy="joined")
    permissions: Mapped[list[Permission]] = relationship(
        secondary="user_permission_rel", lazy="joined"
    )


class UserPermissionRel(models.SQLAlchemyBaseUserPermissionRel, Model):
    pass

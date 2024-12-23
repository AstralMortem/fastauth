from sqlalchemy.orm import DeclarativeBase, Mapped, relationship

from fastauth.contrib.sqlalchemy import models


class Model(DeclarativeBase):
    pass


class Permission(models.SQLAlchemyBasePermission, Model):
    pass


class Role(models.SQLAlchemyBaseRole, Model):
    permissions: Mapped[list[Permission]] = relationship(
        secondary="role_permission_rel", lazy="joined"
    )


class OAuthAccount(models.SQLAlchemyBaseOAuthAccountUUID, Model):
    pass


class User(
    models.SQLAlchemyBaseUserUUID, models.UserRBACMixin, models.UserOAuthMixin, Model
):
    role: Mapped[Role] = relationship(lazy="joined")
    permissions: Mapped[list[Permission]] = relationship(
        secondary="user_permission_rel", lazy="joined"
    )
    oauth_accounts: Mapped[list[OAuthAccount]] = relationship(lazy="joined")


class UserPermissionRel(models.SQLAlchemyBaseUserPermissionRel, Model):
    pass


class RolePermissionRel(models.SQLAlchemyBaseRolePermissionRel, Model):
    pass

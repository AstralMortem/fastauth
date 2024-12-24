import uuid
from typing import TYPE_CHECKING, Generic

from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, declared_attr, mapped_column, relationship

from fastauth.models import ID

from ._generic import GUID


class SQLAlchemyBaseUser(Generic[ID]):
    __tablename__ = "users"

    if TYPE_CHECKING:
        id: ID

    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    username: Mapped[str | None] = mapped_column(String(200), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean(), default=True)
    is_verified: Mapped[bool] = mapped_column(Boolean(), default=False)


class SQLAlchemyBaseUserUUID(SQLAlchemyBaseUser[uuid.UUID]):
    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)


class SQLAlchemyBaseRole:
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    codename: Mapped[str] = mapped_column(unique=True, index=True)

    @declared_attr
    def permissions(self) -> Mapped[list["SQLAlchemyBasePermission"]]:
        return relationship(secondary="role_permission_rel")


class SQLAlchemyBasePermission:
    __tablename__ = "permissions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    codename: Mapped[str] = mapped_column(unique=True, index=True)


class SQLAlchemyBaseRolePermissionRel:
    __tablename__ = "role_permission_rel"

    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"), primary_key=True)
    permission_id: Mapped[int] = mapped_column(
        ForeignKey("permissions.id"), primary_key=True
    )


class SQLAlchemyBaseUserPermissionRel(Generic[ID]):
    __tablename__ = "user_permission_rel"
    user_id: Mapped[ID] = mapped_column(ForeignKey("users.id"), primary_key=True)
    permission_id: Mapped[int] = mapped_column(
        ForeignKey("permissions.id"), primary_key=True
    )


class SQLAlchemyBaseOAuthAccount(Generic[ID]):
    __tablename__ = "oauth_accounts"

    if TYPE_CHECKING:
        id: ID
    oauth_name: Mapped[str] = mapped_column(String(255), index=True)
    access_token: Mapped[str]
    expires_at: Mapped[int | None]
    refresh_token: Mapped[str | None]
    account_id: Mapped[str] = mapped_column(String(200), index=True)
    account_email: Mapped[str] = mapped_column(String(255), index=True)


class SQLAlchemyBaseOAuthAccountUUID(SQLAlchemyBaseOAuthAccount[uuid.UUID]):
    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)

    @declared_attr
    def user_id(self) -> Mapped[GUID]:
        return mapped_column(
            GUID, ForeignKey("users.id", ondelete="cascade"), nullable=False
        )


class UserRBACMixin:
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"))

    @declared_attr
    def role(self) -> Mapped["SQLAlchemyBaseRole"]:
        return relationship()

    @declared_attr
    def permissions(self) -> Mapped[list["SQLAlchemyBasePermission"]]:
        return relationship(secondary="user_permission_rel")


class UserOAuthMixin:
    @declared_attr
    def oauth_accounts(self) -> Mapped["SQLAlchemyBaseOAuthAccount"]:
        return relationship()


__all__ = [
    "UserRBACMixin",
    "UserOAuthMixin",
    "SQLAlchemyBaseUserUUID",
    "SQLAlchemyBaseRole",
    "SQLAlchemyBaseUser",
    "SQLAlchemyBasePermission",
    "SQLAlchemyBaseRolePermissionRel",
    "SQLAlchemyBaseOAuthAccount",
    "SQLAlchemyBaseUserPermissionRel",
    "SQLAlchemyBaseOAuthAccountUUID",
]

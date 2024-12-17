import uuid
from typing import Generic, Optional, List
from fastauth.models import ID
from sqlalchemy.orm import Mapped, mapped_column, relationship, declared_attr
from sqlalchemy import String, Boolean, ForeignKey
from ._generic import GUID


class SQLAlchemyBaseUser(Generic[ID]):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    username: Mapped[Optional[str]] = mapped_column(
        String(200), unique=True, index=True
    )
    hashed_password: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean(), default=True)
    is_verified: Mapped[bool] = mapped_column(Boolean(), default=False)


class SQLAlchemyBaseUserUUID(SQLAlchemyBaseUser[uuid.UUID]):
    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)


class SQLAlchemyBaseRole:
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    codename: Mapped[str] = mapped_column(unique=True, index=True)
    permissions: Mapped["SQLAlchemyBasePermission"] = relationship(
        secondary="role_permission_rel"
    )


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
    oauth_name: Mapped[str] = mapped_column(String(255), index=True)
    access_token: Mapped[str]
    expires_at: Mapped[Optional[int]]
    refresh_token: Mapped[Optional[str]]
    account_id: Mapped[str] = mapped_column(String(200), index=True)
    account_email: Mapped[str] = mapped_column(String(255), index=True)


class SQLAlchemyBaseOAuthAccountUUID(SQLAlchemyBaseOAuthAccount[uuid.UUID]):
    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)

    @declared_attr
    def user_id(cls) -> Mapped[GUID]:
        return mapped_column(
            GUID, ForeignKey("users.id", ondelete="cascade"), nullable=False
        )


class UserRBACMixin:
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"))
    role: Mapped[SQLAlchemyBaseRole] = relationship()
    permissions: Mapped[List[SQLAlchemyBasePermission]] = relationship(
        secondary="user_permission_rel"
    )


class UserOAuthMixin:
    oauth_accounts: Mapped[SQLAlchemyBaseOAuthAccount] = relationship()

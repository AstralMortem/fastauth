import uuid
from typing import Generic, Optional, List, TYPE_CHECKING
from fastauth.models import ID, RP, PP
from sqlalchemy.orm import Mapped, mapped_column, relationship, declared_attr
from sqlalchemy import String, UUID, JSON, ForeignKey, Integer


# Base SQLAlchemy user model
class SQLAlchemyUser(Generic[ID]):
    __tablename__ = "users"
    if TYPE_CHECKING:
        id: ID
        email: str
        username: Optional[str]
        hashed_password: str
        is_active: bool
        is_verified: bool
    else:
        email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
        username: Mapped[Optional[str]] = mapped_column(
            String(255), unique=True, index=True, nullable=True
        )
        hashed_password: Mapped[str] = mapped_column(String(255))
        is_active: Mapped[bool] = mapped_column(default=True)
        is_verified: Mapped[bool] = mapped_column(default=False)


# User model with UUID primary key
class SQLAlchemyUserUUID(SQLAlchemyUser[uuid.UUID]):
    @declared_attr
    def id(self) -> Mapped[uuid.UUID]:
        return mapped_column(UUID(), default=uuid.uuid4, primary_key=True)


class SQLAlchemyPermission:
    __tablename__ = "permissions"
    id: Mapped[int] = mapped_column(Integer(), primary_key=True, autoincrement=True)
    codename: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    detail: Mapped[Optional[JSON]] = mapped_column(JSON())


class SQLAlchemyRole:
    __tablename__ = "roles"
    id: Mapped[int] = mapped_column(Integer(), primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True)

    @declared_attr
    def permissions(self) -> Mapped[List["SQLAlchemyPermission"]]:
        return relationship(secondary="role_permission_rel")


# Mixin to add role to user model
class SQLAlchemyRBACMixin:
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"))

    @declared_attr
    def role(self):
        return relationship("SQLAlchemyRole")


# relation role <- permissions
class SQLAlchemyRolePermissionRel:
    __tablename__ = "role_permission_rel"
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"), primary_key=True)
    permission_id: Mapped[int] = mapped_column(
        ForeignKey("permissions.id"), primary_key=True
    )


class SQLAlchemyOAuthAccount(Generic[ID]):
    __tablename__ = "oauth_accounts"
    if TYPE_CHECKING:  # pragma: no cover
        id: ID
        oauth_name: str
        access_token: str
        expires_at: Optional[int]
        refresh_token: Optional[str]
        account_id: str
        account_email: str
    else:
        oauth_name: Mapped[str] = mapped_column(
            String(length=100), index=True, nullable=False
        )
        access_token: Mapped[str] = mapped_column(String(length=1024), nullable=False)
        expires_at: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
        refresh_token: Mapped[Optional[str]] = mapped_column(
            String(length=1024), nullable=True
        )
        account_id: Mapped[str] = mapped_column(
            String(length=320), index=True, nullable=False
        )
        account_email: Mapped[str] = mapped_column(String(length=320), nullable=False)


class SQLAlchemyOAuthAccountUUID(SQLAlchemyOAuthAccount[uuid.UUID]):
    if TYPE_CHECKING:  # pragma: no cover
        id: uuid.UUID
        user_id: uuid.UUID
    else:
        id: Mapped[uuid.UUID] = mapped_column(
            UUID(), primary_key=True, default=uuid.uuid4
        )

        @declared_attr
        def user_id(cls) -> Mapped[UUID]:
            return mapped_column(
                UUID(), ForeignKey("users.id", ondelete="cascade"), nullable=False
            )

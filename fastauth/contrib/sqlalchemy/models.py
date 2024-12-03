import uuid
from typing import Generic, Optional, List, TYPE_CHECKING
from fastauth.models import ID
from sqlalchemy.orm import Mapped, mapped_column, relationship, declared_attr
from sqlalchemy import String, UUID, JSON, ForeignKey, Integer


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


class SQLAlchemyUserUUID(SQLAlchemyUser[uuid.UUID]):
    @declared_attr
    def id(self) -> Mapped[uuid.UUID]:
        return mapped_column(UUID(), default=uuid.uuid4, primary_key=True)


class SQLAlchemyRole:
    __tablename__ = "roles"
    id: Mapped[int] = mapped_column(Integer(), primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True)

    @declared_attr
    def permissions(self) -> Mapped[List["SQLAlchemyPermission"]]:
        return relationship(secondary="role_permission_rel")


class SQLAlchemyPermission:
    __tablename__ = "permissions"
    id: Mapped[int] = mapped_column(Integer(), primary_key=True, autoincrement=True)
    codename: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    detail: Mapped[Optional[JSON]] = mapped_column(JSON())


class SQLAlchemyRBACMixin:
    @declared_attr
    def roles(self):
        return relationship(Mapped[List[SQLAlchemyRole]], secondary="user_role_rel")

    @declared_attr
    def permissions(self):
        return relationship(
            Mapped[List[SQLAlchemyPermission]], secondary="user_permission_rel"
        )


# relation role <- permissions


class SQLAlchemyRolePermissionRel:
    __tablename__ = "role_permission_rel"
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"), primary_key=True)
    permission_id: Mapped[int] = mapped_column(
        ForeignKey("permissions.id"), primary_key=True
    )


# relation user <- roles


class SQLAlchemyUserRoleRel(Generic[ID]):
    __tablename__ = "user_role_rel"
    user_id: Mapped[ID] = mapped_column(ForeignKey("users.id"), primary_key=True)
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"), primary_key=True)


# relation user <- permissions


class SQLAlchemyUserPermissionRel(Generic[ID]):
    __tablename__ = "user_permission_rel"
    user_id: Mapped[ID] = mapped_column(ForeignKey("users.id"), primary_key=True)
    permission_id: Mapped[int] = mapped_column(
        ForeignKey("permissions.id"), primary_key=True
    )

# SQLAlchemy models

## User model
As for any SQLAlchemy ORM model, we'll create `User` model.
```python
from fastauth.contrib.sqlalchemy import SQLAlchemyBaseUserUUID
from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

DATABASE_URL = "sqlite+aiosqlite:///./test.db"
engine = create_async_engine(DATABASE_URL)
sessionmaker = async_sessionmaker(engine)

class Model(DeclarativeBase):
    pass

class User(SQLAlchemyBaseUserUUID, Model):
    pass

async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with sessionmaker() as session:
        yield session

```

!!! tip "Primary key is defined as UUID"
    By default, we use UUID as a primary key ID for your user. If you want to use another type, like an auto-incremented integer, you can use `SQLAlchemyBaseUser` as base class and define your own id column.
    ```python
    class User(SQLAlchemyBaseUser[int], Model):
        id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ```
    Notice that SQLAlchemyBaseUser expects a generic type to define the actual type of ID you use.

## Role and Permission models

To create Role and Permission models, and bind them with User model, we need to:

```python hl_lines="12-16"
from fastauth.contrib.sqlalchemy import SQLAlchemyBaseRole, SQLAlchemyBasePermission, \
SQLAlchemyBaseRolePermissionRel, SQLAlchemyBaseUserUUID, UserRBACMixin, SQLAlchemyBaseUserPermissionRel
from sqlalchemy.orm import Mapped, relationship
from typing import List
from sqlalchemy.orm import DeclarativeBase


class Model(DeclarativeBase):
    pass


class User(SQLAlchemyBaseUserUUID, UserRBACMixin, Model):
    role: Mapped["Role"] = relationship(lazy="joined")
    permissions: Mapped[List["Permission"]] = relationship(
        secondary="user_permission_rel", lazy="joined"
    )


class Role(SQLAlchemyBaseRole):
    permissions: Mapped[List["Permission"]] = relationship(
        secondary="role_permission_rel", lazy="joined"
    )

class Permission(SQLAlchemyBasePermission, Model):
    pass


# Many-to-many relation between Role and Permission
# __tablename__ = 'role_permission_rel'
class RolePermission(SQLAlchemyBaseRolePermissionRel, Model):
    pass

# Many-to-many relation between User and Permission
# __tablename__ = 'user_permission_rel'
class UserPermission(SQLAlchemyBaseUserPermissionRel, Model):
    pass

```

As we see, we create new models `Role` and `Permission`, then we modify `User` model by inherit `UserRBACMixin` to bind
RBAC to User. Also, we create Many-to-many relation between models.

## OAuth account model
Not Implemented

To create OAuth accounts model, and bind it with User model, we need to:

```python hl_lines="11 12"
from fastauth.contrib.sqlalchemy import SQLAlchemyBaseUserUUID, SQLAlchemyBaseOAuthAccountUUID, UserOAuthMixin
from sqlalchemy.orm import Mapped, relationship
from typing import List
from sqlalchemy.orm import DeclarativeBase


class Model(DeclarativeBase):
    pass


class User(SQLAlchemyBaseUserUUID, UserOAuthMixin, Model):
    oauth_accounts: Mapped[List["OAuthAccount"]] = relationship(lazy="joined")


class OAuthAccount(SQLAlchemyBaseOAuthAccountUUID, Model):
    pass

```
We create OAuthAccount Model, and modify User model by inheriting `UserOAuthMixin`, then set Mapper to bind
then together


!!! tip "Primary key is defined as UUID"
    By default, we use UUID as a primary key ID for OAuthAccount. If you want to use another type, like an auto-incremented integer, you can use `SQLAlchemyBaseOAuthAccount` as base class and define your own id column.
    ```python
    class OAuthAccount(SQLAlchemyBaseOAuthAccount[int], Model):
        id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ```
    Notice that SQLAlchemyBaseOAuthAccount expects a generic type to define the actual type of ID you use.


## Full model
And of course we can combine all mixins to get full featured models, so if we want OAuth2 with RBAC support, we need modify our user model:
```python hl_lines="3-8"
    ...

class User(SQLAlchemyBaseUserUUID,UserRBACMixin, UserOAuthMixin, Model):
    role: Mapped["Role"] = relationship(lazy="joined")
    permissions: Mapped[List["Permission"]] = relationship(
        secondary="user_permission_rel", lazy="joined"
    )
    oauth_accounts: Mapped[List["OAuthAccount"]] = relationship(lazy="joined")

    ...

```
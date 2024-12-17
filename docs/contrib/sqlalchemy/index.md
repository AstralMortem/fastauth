# SQLAlchemy
FastAuth provides the necessary tools to work with SQL databases thanks to SQLAlchemy ORM with asyncio.
To work with your DBMS, you'll need to install the corresponding asyncio driver. The common choices are:

  * For PostgreSQL: `pip install asyncpg`
  * For SQLite: `pip install aiosqlite`

**Let see full SQLAlchemy example**

=== "models.py"
    ```python
    from sqlalchemy.orm import DeclarativeBase
    from fastauth.contrib.sqlalchemy import models

    class Model(DeclarativeBase):
        pass

    class User(models.SQLAlchemyBaseUserUUID, models.UserRBACMixin, Model):
        role: Mapped["Role"] = relationship(lazy="joined")
        permissions: Mapped[List["Permission"]] = relationship(
            secondary="user_permission_rel", lazy="joined"
        )

    class Role(models.SQLAlchemyBaseRole, Model):
        permissions: Mapped[List["Permission"]] = relationship(
            secondary="role_permission_rel", lazy="joined"
        )
    
    
    class Permission(models.SQLAlchemyBasePermission, Model):
        pass
    
    
    class RolePermission(models.SQLAlchemyBaseRolePermissionRel, Model):
        pass
    
    
    class UserPermission(models.SQLAlchemyBaseUserPermissionRel, Model):
        pass
    ```
=== "repository.py"
    ```python
    from fastauth.contrib.sqlalchemy import repositories
    from models import User, Role, Permission
    
    class UserRepository(repositories.SQLAlchemyUserRepository[User, uuid.UUID]):
        user_model = User
    
    
    class RBACRepository(repositories.SQLAlchemyRBACRepository[Role, Permission]):
        role_model = Role
        permission_model = Permission
    ```

=== "manager.py"
    ```python
    import uuid
    from repository import UserRepository, RBACRepository
    from fastauth.manager import BaseAuthManager
    from fastauth.config import FastAuthConfig
    from fastauth.strategy import JWTStrategy
    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
    
    engine = create_async_engine("sqlite+aiosqlite:///db.db")
    session = async_sessionmaker(engine)

    async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with sessionmaker() as session:
        yield session


    config = FastAuthConfig()


    class AuthManager(BaseAuthManager[User, uuid.UUID]):
        def parse_id(self, pk: str):
            return uuid.UUID(pk)
    
    security = FastAuth(config)

    @security.set_auth_callback
    async def auth_callback(
        config: FastAuthConfig, session: AsyncSession = Depends(get_db)
    ):
        return AuthManager(config, UserRepository(session), RBACRepository(session))


    @security.set_token_strategy
    async def token_strategy(config: FastAuthConfig):
        return JWTStrategy(config)

    ```



=== "schema.py"
    test

=== "app.py"
    ```python
    ```
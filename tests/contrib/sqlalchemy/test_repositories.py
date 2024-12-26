import asyncio
import contextlib
from typing import AsyncIterator, Callable
from uuid import UUID
from fastauth.contrib.sqlalchemy import models, repositories, SQLAlchemyUserRepository
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, relationship
import pytest
from fastauth.utils.injector import injectable
from fastapi import Depends


class Model(DeclarativeBase):
    pass


class User(
    models.SQLAlchemyBaseUserUUID, models.UserRBACMixin, models.UserOAuthMixin, Model
):
    role: Mapped["Role"] = relationship(lazy="joined")
    permissions: Mapped[list["Permission"]] = relationship(
        secondary="user_permission_rel", lazy="joined"
    )
    oauth_accounts: Mapped[list["OAuthAccount"]] = relationship(
        lazy="joined", cascade="all, delete"
    )


class Role(models.SQLAlchemyBaseRole, Model):
    permissions: Mapped[list["Permission"]] = relationship(
        secondary="role_permission_rel", lazy="joined"
    )


class Permission(models.SQLAlchemyBasePermission, Model):
    pass


class UserPermissionRel(models.SQLAlchemyBaseUserPermissionRel, Model):
    pass


class RolePermission(models.SQLAlchemyBaseRolePermissionRel, Model):
    pass


class OAuthAccount(models.SQLAlchemyBaseOAuthAccountUUID, Model):
    pass


@pytest.fixture(scope="function")
@contextlib.asynccontextmanager
async def session() -> AsyncSession:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Model.metadata.create_all)
    AsyncSessionLocal = async_sessionmaker(
        bind=engine, class_=AsyncSession, expire_on_commit=False
    )

    async with AsyncSessionLocal() as session:
        try:
            p1 = Permission(id=1, codename="user:read")
            p2 = Permission(id=2, codename="user:create")
            p3 = Permission(id=3, codename="admin:delete")
            p4 = Permission(id=4, codename="admin:update")
            p5 = Permission(id=5, codename="user:delete")
            test_data = [
                p1,
                p2,
                p3,
                p4,
                p5,
                Role(id=1, codename="USER", permissions=[p1, p2]),
                Role(id=2, codename="ADMIN", permissions=[p3, p4]),
                User(
                    id=UUID("59f99030-88fa-42a1-8750-9119419963ce"),
                    email="user1@example.com",
                    username="user1",
                    hashed_password="password",
                    is_active=True,
                    is_verified=True,
                    role_id=1,
                    permissions=[p5],
                ),
                User(
                    id=UUID("e3e47658-ff6f-4682-aa6a-be359c313623"),
                    email="user2@example.com",
                    username="user2",
                    hashed_password="password",
                    is_active=True,
                    is_verified=True,
                    role_id=2,
                    permissions=[p5],
                ),
                OAuthAccount(
                    id=UUID("1d155c85-90ed-446a-beb8-1a675daa83f7"),
                    user_id=UUID("59f99030-88fa-42a1-8750-9119419963ce"),
                    account_id="1234",
                    account_email="user1@example.com",
                    oauth_name="github",
                    access_token="token",
                ),
            ]
            session.add_all(test_data)
            await session.commit()

            yield session
        except Exception as e:
            await session.rollback()
            raise e
        finally:
            await session.close()

    async with engine.begin() as conn:
        await conn.run_sync(Model.metadata.drop_all)
    await engine.dispose()


@pytest.fixture
@contextlib.asynccontextmanager
async def user_repo(
    session,
) -> AsyncIterator[SQLAlchemyUserRepository[User, UUID]]:
    async with session as Session:
        instance = repositories.SQLAlchemyUserRepository(Session)
        instance.user_model = User
        yield instance


@pytest.fixture
@contextlib.asynccontextmanager
async def rbac_repo(session):
    async with session as Session:
        instance = repositories.SQLAlchemyRBACRepository(Session)
        instance.role_model = Role
        instance.permission_model = Permission
        yield instance


@pytest.fixture
@contextlib.asynccontextmanager
async def oauth_repo(session):
    async with session as Session:
        instance = repositories.SQLAlchemyOAuthRepository(Session)
        instance.user_model = User
        instance.oauth_model = OAuthAccount
        yield instance


# TESTS
@pytest.mark.asyncio
async def test_user_repo_get_user(user_repo):
    uid = UUID("59f99030-88fa-42a1-8750-9119419963ce")
    email = "user1@example.com"
    username = "user1"

    async with user_repo as repo:
        user = await repo.get_by_id(uid)
        assert user.email == email

        user = await repo.get_by_email(email)
        assert user.id == uid

        user = await repo.get_by_username(username)
        assert user.id == uid

        user = await repo.get_by_field("username", username)
        assert user.id == uid

        user = await repo.get_by_fields(["email", "username"], username)
        assert user.id == uid


@pytest.mark.asyncio
async def test_user_creation(user_repo):
    async with user_repo as repo:
        user = await repo.create(
            {"email": "user3@example.com", "hashed_password": "password", "role_id": 1}
        )

        assert type(user.id) is UUID
        assert user.email == "user3@example.com"


@pytest.mark.asyncio
async def test_user_update(user_repo):
    async with user_repo as repo:
        user = await repo.get_by_email("user1@example.com")
        user = await repo.update(user, {"email": "user4@example.com"})
        assert user.email == "user4@example.com"

        with pytest.raises(Exception):
            new_user = await repo.update(user, {"email": "user2@example.com"})


@pytest.mark.asyncio
async def test_user_deletion(user_repo):
    async with user_repo as repo:
        user = await repo.get_by_email("user1@example.com")
        await repo.delete(user)

        old_user = await repo.get_by_email("user1@example.com")
        assert old_user is None


@pytest.mark.asyncio
async def test_rbac_repo_get(rbac_repo):
    async with rbac_repo as repo:
        role = await repo.get_role_by_id(1)
        assert role.codename == "USER"

        role = await repo.get_role_by_codename("USER")
        assert role.id == 1

        permission = await repo.get_permission_by_id(1)
        assert permission.codename == "user:read"

        permission = await repo.get_permission_by_codename("user:read")
        assert permission.id == 1

        list_roles = await repo.list_roles()
        assert len(list_roles) == 2

        permission_list = await repo.list_permissions()
        assert len(permission_list) == 5


@pytest.mark.asyncio
async def test_rbac_repo_creation(rbac_repo):
    async with rbac_repo as repo:

        permission = await repo.create_permission({"codename": "staff:update"})
        assert permission.codename == "staff:update"

        role = await repo.create_role(
            {"codename": "STAFF", "permissions": [permission]}
        )
        assert role.codename == "STAFF"
        assert role.permissions[0] == permission

        with pytest.raises(Exception):
            await repo.create_role({"codename": "ADMIN"})

        with pytest.raises(Exception):
            await repo.create_permission({"codename": "user:read"})


@pytest.mark.asyncio
async def test_rbac_repo_update(rbac_repo):
    async with rbac_repo as repo:
        role = await repo.get_role_by_codename("USER")
        role = await repo.update_role(role, {"codename": "SUPERUSER"})
        assert role.codename == "SUPERUSER"

        permission = await repo.get_permission_by_id(1)
        permission = await repo.update_permission(
            permission, {"codename": "superuser:read"}
        )
        assert permission.codename == "superuser:read"

        with pytest.raises(Exception):
            await repo.update_role(role, {"codename": "ADMIN"})

        with pytest.raises(Exception):
            await repo.update_permission(permission, {"codename": "user:update"})


@pytest.mark.asyncio
async def test_rbac_repo_deletion(rbac_repo):
    async with rbac_repo as repo:
        role = await repo.get_role_by_codename("USER")
        await repo.delete_role(role)

        old_role = await repo.get_role_by_codename("USER")
        assert old_role is None

        permission = await repo.get_permission_by_codename("user:read")
        await repo.delete_permission(permission)

        old_permission = await repo.get_permission_by_codename("user:read")
        assert old_permission is None


@pytest.mark.asyncio
async def test_oauth_repo_get_user(oauth_repo):
    async with oauth_repo as repo:
        user = await repo.get_user("github", "1234")
        assert user.email == "user1@example.com"


@pytest.mark.asyncio
async def test_oauth_repo_add_account(oauth_repo):
    async with oauth_repo as repo:
        user = await repo.get_user("github", "1234")

        user = await repo.add_oauth_account(
            user,
            {
                "account_id": "5678",
                "account_email": user.email,
                "oauth_name": "google",
                "access_token": "access_token",
            },
        )

        assert user.email == "user1@example.com"
        assert len(user.oauth_accounts) == 2


@pytest.mark.asyncio
async def test_oauth_repo_update_account(oauth_repo):
    async with oauth_repo as repo:
        user = await repo.get_user("github", "1234")

        user = await repo.update_oauth_account(
            user, user.oauth_accounts[0], {"oauth_name": "google"}
        )
        assert user.email == "user1@example.com"
        assert user.oauth_accounts[0].oauth_name == "google"

        user = await repo.get_user("github", "1234")
        assert user is None

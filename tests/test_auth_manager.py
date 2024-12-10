import pytest
from fastapi import HTTPException
from unittest.mock import AsyncMock, MagicMock
from fastauth.manager import BaseAuthManager
from fastauth.config import FastAuthConfig
from fastauth.repositories import (
    AbstractUserRepository,
    AbstractRoleRepository,
    AbstractPermissionRepository,
    AbstractOAuthRepository,
)
from fastauth.schemas import BaseUserCreate
from fastauth.utils.password import PasswordHelper
from fastauth import exceptions


@pytest.fixture
def config():
    return FastAuthConfig()


@pytest.fixture
def user_repository():
    return AsyncMock(spec=AbstractUserRepository)


@pytest.fixture
def roles_repository():
    return AsyncMock(spce=AbstractRoleRepository)


@pytest.fixture
def perm_repository():
    return AsyncMock(spec=AbstractPermissionRepository)


@pytest.fixture
def oauth_repository():
    return AsyncMock(spec=AbstractOAuthRepository)


@pytest.fixture
def password_helper():
    return AsyncMock(spec=PasswordHelper)


@pytest.fixture
def auth_manager(
    config,
    user_repository,
    roles_repository,
    perm_repository,
    oauth_repository,
    password_helper,
):
    return BaseAuthManager(
        config=config,
        user_repository=user_repository,
        role_repository=roles_repository,
        permission_repository=perm_repository,
        oauth_repository=oauth_repository,
        password_helper=password_helper,
    )


@pytest.mark.asyncio
async def test_get_user(auth_manager):
    pass


@pytest.mark.asyncio
async def test_get_user_not_exists(auth_manager, user_repository):
    user_repository.get_by_id.return_value = None
    with pytest.raises(exceptions.UserNotExists):
        await auth_manager.get_user(1)
    user_repository.get_by_id.assert_called_once_with(1)


@pytest.mark.asyncio
async def test_create_user_with_default_role_when_rbac_enabled(auth_manager):
    config = FastAuthConfig(ENABLE_RBAC=True, DEFAULT_USER_REGISTER_ROLE="user")

    auth_manager._config = config
    auth_manager.user_repo.get_by_email.return_value = None
    auth_manager.role_repo.get_by_name.return_value = MagicMock(id=1)
    auth_manager.user_repo.create.return_value = MagicMock(
        id=1, email="test@example.com"
    )
    auth_manager.password_helper.hash.return_value = "hashed_password"

    user_create = BaseUserCreate(email="test@example.com", password="password123")
    new_user = await auth_manager.create_user(user_create)

    # auth_manager.role_repo.get_by_name.assert_called_once_with("user")
    # auth_manager.user_repo.create.assert_called_once_with(
    #     {
    #         "email": "test@example.com",
    #         "hashed_password": "hashed_password",
    #         "role_id": 1,
    #     }
    # )
    assert new_user.id == 1
    assert new_user.email == "test@example.com"

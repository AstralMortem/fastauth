from unittest.mock import AsyncMock, MagicMock

import pytest

from fastauth import exceptions
from fastauth.exceptions import RoleNotFound
from fastauth.manager import BaseAuthManager
from fastauth.repositories import (
    AbstractUserRepository,
    AbstractRolePermissionRepository,
)
from fastauth.schema import BaseRoleCreate, BaseRoleUpdate


@pytest.fixture
def auth_manager(fastauth_config):
    manager = BaseAuthManager(
        config=fastauth_config,
        user_repository=AsyncMock(spec=AbstractUserRepository),
        rp_repository=AsyncMock(spec=AbstractRolePermissionRepository),
        oauth_repository=None,
    )
    return manager


@pytest.mark.asyncio
async def test_get_role_id(auth_manager):
    auth_manager.rp_repo.get_role_by_id = AsyncMock(return_value=123)
    result = await auth_manager.get_role(123)
    assert result == 123

    with pytest.raises(exceptions.RoleNotFound):
        auth_manager.rp_repo.get_role_by_id = AsyncMock(return_value=None)
        await auth_manager.get_role(456)


@pytest.mark.asyncio
async def test_get_role_by_codename(auth_manager):
    auth_manager.rp_repo.get_role_by_codename = AsyncMock(return_value=123)
    result = await auth_manager.get_role_by_codename("admin")
    assert result == 123

    with pytest.raises(RoleNotFound):
        auth_manager.rp_repo.get_role_by_codename = AsyncMock(return_value=None)
        await auth_manager.get_role_by_codename("guest")


@pytest.mark.asyncio
async def test_role_creation(auth_manager):
    role_data = BaseRoleCreate(codename="test")
    auth_manager.rp_repo.create_role = AsyncMock(side_effect=lambda role: role)
    role = await auth_manager.create_role(role_data)
    assert role == role_data.model_dump()


@pytest.mark.asyncio
async def test_role_update(auth_manager):
    role_data = BaseRoleUpdate(codename="test")
    auth_manager.rp_repo.update_role = AsyncMock(side_effect=lambda role, data: data)
    role = await auth_manager.update_role(123, role_data)
    assert role == role_data.model_dump(exclude_unset=True, exclude_defaults=True)


@pytest.mark.asyncio
async def test_role_deletion(auth_manager):
    auth_manager.rp_repo.delete_role = AsyncMock()
    result = await auth_manager.delete_role(123)
    assert result == None


@pytest.mark.asyncio
async def test_role_list(auth_manager):
    auth_manager.rp_repo.list_roles = AsyncMock(return_value=[])
    result = await auth_manager.list_role()
    assert result == []


@pytest.mark.asyncio
async def test_assign_role_to_user(auth_manager):
    auth_manager.rp_repo.get_role_by_id.return_value = MagicMock(id=1)
    auth_manager.user_repo.get_by_id.return_value = MagicMock(id="user-id")

    async def update(user, data):
        for k, v in data.items():
            setattr(user, k, v)
        return user

    auth_manager.user_repo.update.side_effect = update

    result = await auth_manager.assign_role_to_user("user-id", 1)

    assert result.id == "user-id"
    assert result.role_id == 1

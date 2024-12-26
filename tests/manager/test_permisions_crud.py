from unittest.mock import AsyncMock
import pytest
from fastauth import exceptions
from fastauth.manager import BaseAuthManager
from fastauth.repositories import (
    AbstractUserRepository,
    AbstractRolePermissionRepository,
)
from fastauth.schema import BasePermissionCreate


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
async def test_get_permission_id(auth_manager):
    auth_manager.rp_repo.get_permission_by_id = AsyncMock(return_value=123)
    result = await auth_manager.get_permission(123)
    assert result == 123

    with pytest.raises(exceptions.PermissionNotFound):
        auth_manager.rp_repo.get_permission_by_id = AsyncMock(return_value=None)
        await auth_manager.get_permission(456)


@pytest.mark.asyncio
async def test_get_permission_by_codename(auth_manager):
    auth_manager.rp_repo.get_permission_by_codename = AsyncMock(return_value=123)
    result = await auth_manager.get_permission_by_codename("admin")
    assert result == 123

    with pytest.raises(exceptions.PermissionNotFound):
        auth_manager.rp_repo.get_permission_by_codename = AsyncMock(return_value=None)
        await auth_manager.get_permission_by_codename("guest")


@pytest.mark.asyncio
async def test_permission_creation(auth_manager):
    permission_data = BasePermissionCreate(codename="test")
    auth_manager.rp_repo.create_permission = AsyncMock(
        side_effect=lambda permission: permission
    )
    permission = await auth_manager.create_permission(permission_data)
    assert permission == permission_data.model_dump()


@pytest.mark.asyncio
async def test_permission_update(auth_manager):
    permission_data = BasePermissionCreate(codename="test")
    auth_manager.rp_repo.update_permission = AsyncMock(
        side_effect=lambda permission, data: data
    )
    permission = await auth_manager.update_permission(123, permission_data)
    assert permission == permission_data.model_dump(
        exclude_unset=True, exclude_defaults=True
    )


@pytest.mark.asyncio
async def test_permission_deletion(auth_manager):
    auth_manager.rp_repo.delete_permission = AsyncMock()
    result = await auth_manager.delete_permission(123)
    assert result == None


@pytest.mark.asyncio
async def test_permission_list(auth_manager):
    auth_manager.rp_repo.list_permissions = AsyncMock(return_value=[])
    result = await auth_manager.list_permission()
    assert result == []

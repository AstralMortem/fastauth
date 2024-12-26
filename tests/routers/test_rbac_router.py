import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock, Mock

from fastauth.routers.rbac import get_roles_router, get_permissions_router
from fastauth.schema.base import BaseSchema


# Mock dependencies
@pytest.fixture
def mock_security(fastauth_config, fastauth, token_strategy):
    fastauth_config.ROUTER_ROLES_DEFAULT_PREFIX = "/roles"
    fastauth_config.ROUTER_PERMISSIONS_DEFAULT_PREFIX = "/permissions"
    fastauth_config.ADMIN_DEFAULT_ROLE = "admin"
    fastauth_config.USER_DEFAULT_IS_ACTIVE = True
    fastauth_config.USER_DEFAULT_IS_VERIFIED = True

    token_strategy.read_token.return_value = {"type": "access"}
    # fastauth.user_required = Mock(return_value=AsyncMock(return_value=True))

    return fastauth


@pytest.fixture
def mock_manager(auth_manager):
    auth_manager.get_role = AsyncMock(return_value={"id": 1, "name": "role1"})
    auth_manager.get_permission = AsyncMock(return_value={"id": 1, "name": "perm1"})
    return auth_manager


@pytest.fixture
def app(mock_security, auth_manager):
    app = FastAPI()

    # Role and Permission schemas for testing
    class MockRoleSchema(BaseSchema):
        id: int | None = None
        name: str

    class MockPermissionSchema(BaseSchema):
        id: int | None = None
        name: str

    # Include routers
    app.include_router(
        get_roles_router(
            security=mock_security,
            role_read=MockRoleSchema,
            role_create=MockRoleSchema,
            role_update=MockRoleSchema,
        )
    )
    app.include_router(
        get_permissions_router(
            security=mock_security,
            permission_read=MockPermissionSchema,
            permission_create=MockPermissionSchema,
            permission_update=MockPermissionSchema,
        )
    )
    return app


@pytest.fixture
def test_client(app):
    return TestClient(app)


# Tests for Roles Router
def test_get_role(test_client, auth_manager):
    role = {"id": 1, "name": "role1"}
    auth_manager.get_role.return_value = role
    auth_manager.get_role_by_codename.return_value = role
    auth_manager.list_role.return_value = [role]

    response = test_client.get(
        "/roles/1", headers={"Authorization": "Bearer access_token"}
    )
    assert response.status_code == 200
    assert response.json() == role

    response = test_client.get(
        "/roles/role1", headers={"Authorization": "Bearer access_token"}
    )
    assert response.status_code == 200
    assert response.json() == role

    response = test_client.get(
        "/roles", headers={"Authorization": "Bearer access_token"}
    )
    assert response.status_code == 200
    assert response.json() == [role]


def test_create_role(test_client, auth_manager):
    auth_manager.create_role.return_value = {"id": 2, "name": "new_role"}
    response = test_client.post(
        "/roles/",
        json={"name": "new_role"},
        headers={"Authorization": "Bearer access_token"},
    )
    assert response.status_code == 200
    assert response.json() == {"id": 2, "name": "new_role"}


def test_update_role(test_client, auth_manager):
    auth_manager.update_role.return_value = {"id": 1, "name": "new_role"}
    response = test_client.patch(
        "/roles/1",
        json={"name": "new_role"},
        headers={"Authorization": "Bearer access_token"},
    )
    assert response.status_code == 200
    assert response.json() == {"id": 1, "name": "new_role"}


def test_delete_role(test_client, auth_manager):
    auth_manager.delete_role.return_value = None
    response = test_client.delete(
        "/roles/1", headers={"Authorization": "Bearer access_token"}
    )
    assert response.status_code == 200


# Tests for Roles Router
def test_get_permission(test_client, auth_manager):
    permission = {"id": 1, "name": "permission1"}
    auth_manager.get_permission.return_value = permission
    auth_manager.get_permission_by_codename.return_value = permission
    auth_manager.list_permission.return_value = [permission]

    response = test_client.get(
        "/permissions/1", headers={"Authorization": "Bearer access_token"}
    )
    assert response.status_code == 200
    assert response.json() == permission

    response = test_client.get(
        "/permissions/permission1", headers={"Authorization": "Bearer access_token"}
    )
    assert response.status_code == 200
    assert response.json() == permission

    response = test_client.get(
        "/permissions", headers={"Authorization": "Bearer access_token"}
    )
    assert response.status_code == 200
    assert response.json() == [permission]


def test_create_permission(test_client, auth_manager):
    auth_manager.create_permission.return_value = {"id": 2, "name": "new_permission"}
    response = test_client.post(
        "/permissions/",
        json={"name": "new_permission"},
        headers={"Authorization": "Bearer access_token"},
    )
    assert response.status_code == 200
    assert response.json() == {"id": 2, "name": "new_permission"}


def test_update_permission(test_client, auth_manager):
    auth_manager.update_permission.return_value = {"id": 1, "name": "new_permission"}
    response = test_client.patch(
        "/permissions/1",
        json={"name": "new_permission"},
        headers={"Authorization": "Bearer access_token"},
    )
    assert response.status_code == 200
    assert response.json() == {"id": 1, "name": "new_permission"}


def test_delete_permission(test_client, auth_manager):
    auth_manager.delete_permission.return_value = None
    response = test_client.delete(
        "/permissions/1", headers={"Authorization": "Bearer access_token"}
    )
    assert response.status_code == 200

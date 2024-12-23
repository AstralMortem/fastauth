from fastapi import APIRouter, Depends

from fastauth.fastauth import FastAuth
from fastauth.schema import PC_S, PR_S, PU_S, RC_S, RR_S, RU_S


def _admin_dep(security, default_admin_role, is_active, is_verified):
    admin_role = default_admin_role or security.config.ADMIN_DEFAULT_ROLE
    is_active = is_active or security.config.USER_DEFAULT_IS_ACTIVE
    is_verified = is_verified or security.config.USER_DEFAULT_IS_VERIFIED

    dependency = Depends(
        security.user_required(
            roles=[admin_role], is_active=is_active, is_verified=is_verified
        )
    )
    return dependency


def get_roles_router(
    security: FastAuth,
    role_read: type[RR_S],
    role_create: type[RC_S],
    role_update: type[RU_S],
    default_admin_role: str | None = None,
    is_active: bool | None = None,
    is_verified: bool | None = None,
):
    router = APIRouter(prefix=security.config.ROUTER_ROLES_DEFAULT_PREFIX)
    admin_dep = _admin_dep(security, default_admin_role, is_active, is_verified)

    @router.get("/{id}", dependencies=[admin_dep], response_model=role_read)
    async def get_role(id: int, manager=security.AUTH_MANAGER):
        return await manager.get_role(id)

    @router.get("/{codename}", dependencies=[admin_dep], response_model=role_read)
    async def get_role_by_codename(codename: str, manager=security.AUTH_MANAGER):
        return await manager.get_role_by_codename(codename)

    @router.post("/", dependencies=[admin_dep], response_model=role_read)
    async def create_role(data: role_create, manager=security.AUTH_MANAGER):
        return await manager.create_role(data)

    @router.patch("/{id}", dependencies=[admin_dep], response_model=role_read)
    async def update_role(id: int, data: role_update, manager=security.AUTH_MANAGER):
        return await manager.update_role(id, data)

    @router.delete("/{id}", dependencies=[admin_dep], response_model=role_read)
    async def delete_role(id: int, manager=security.AUTH_MANAGER):
        return await manager.delete_role(id)

    @router.get("/", dependencies=[admin_dep], response_model=list[role_read])
    async def list_role(manager=security.AUTH_MANAGER):
        return await manager.list_role()

    @router.post("/{id}/assign_user/{user_id}", dependencies=[admin_dep])
    async def assign_role_to_user(id: int, user_id: str, manager=security.AUTH_MANAGER):
        await manager.assign_role_to_user(id, user_id)
        return None

    return router


def get_permissions_router(
    security: FastAuth,
    permission_read: type[PR_S],
    permission_create: type[PU_S],
    permission_update: type[PC_S],
    default_admin_role: str | None = None,
    is_active: bool | None = None,
    is_verified: bool | None = None,
):
    router = APIRouter(prefix=security.config.ROUTER_PERMISSIONS_DEFAULT_PREFIX)
    admin_dep = _admin_dep(security, default_admin_role, is_active, is_verified)

    @router.get("/{id}", dependencies=[admin_dep], response_model=permission_read)
    async def get_permission(id: int, manager=security.AUTH_MANAGER):
        return await manager.get_permission(id)

    @router.get("/{codename}", dependencies=[admin_dep], response_model=permission_read)
    async def get_permission_by_codename(codename: str, manager=security.AUTH_MANAGER):
        return await manager.get_permission_by_codename(codename)

    @router.post("/", dependencies=[admin_dep], response_model=permission_read)
    async def create_permission(data: permission_create, manager=security.AUTH_MANAGER):
        return await manager.create_permission(data)

    @router.patch("/{id}", dependencies=[admin_dep], response_model=permission_read)
    async def update_permission(
        id: int, data: permission_update, manager=security.AUTH_MANAGER
    ):
        return await manager.update_permission(id, data)

    @router.delete("/{id}", dependencies=[admin_dep], response_model=permission_read)
    async def delete_permission(id: int, manager=security.AUTH_MANAGER):
        return await manager.delete_permission(id)

    @router.get("/", dependencies=[admin_dep], response_model=list[permission_read])
    async def list_permission(manager=security.AUTH_MANAGER):
        return await manager.list_permission()

    return router

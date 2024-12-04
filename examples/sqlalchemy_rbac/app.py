from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastauth.routers import FastAuthRouter
from .dependencies import security
from examples.db import sessionmanager
from .models import Model, Permission
from .schemas import (
    RoleRead,
    RoleUpdate,
    RoleCreate,
    UserRead,
    UserCreate,
    UserUpdate,
    PermissionRead,
    PermissionCreate,
    PermissionUpdate,
)


@asynccontextmanager
async def init_db(app: FastAPI):
    async with sessionmanager.connect() as conn:
        await conn.run_sync(Model.metadata.create_all)
        yield
        await conn.close()


app = FastAPI(lifespan=init_db)
auth_router = FastAuthRouter(security)


app.include_router(auth_router.get_auth_router(), tags=["Auth"])
app.include_router(auth_router.get_register_router(UserRead, UserCreate), tags=["Auth"])
app.include_router(
    auth_router.get_users_router(UserRead, UserCreate, UserUpdate), tags=["Users"]
)
app.include_router(
    auth_router.get_roles_router(RoleRead, RoleCreate, RoleUpdate), tags=["Roles"]
)
app.include_router(
    auth_router.get_permission_router(
        PermissionRead, PermissionCreate, PermissionUpdate
    ),
    tags=["Permissions"],
)

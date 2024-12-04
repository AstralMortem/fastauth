from contextlib import asynccontextmanager
from fastapi import FastAPI
from .dependencies import security
from .models import Model
from examples.db import sessionmanager
from fastauth.routers import FastAuthRouter
from .oauth_client import github_client
from .schema.user import UserRead, UserCreate, UserUpdate
from .schema.roles import RoleRead, RoleCreate, RoleUpdate
from .schema.permission import PermissionRead, PermissionUpdate, PermissionCreate


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
app.include_router(auth_router.get_verify_router(UserRead), tags=["Auth"])
app.include_router(auth_router.get_password_router(), tags=["Auth"])
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

app.include_router(auth_router.get_oauth_router(github_client), tags=["OAuth"])

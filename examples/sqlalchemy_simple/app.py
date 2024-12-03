from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends
from .dependency import security, config

from fastauth.routers import FastAuthRouter
from .schema import UserRead, UserCreate, UserUpdate
from .models import Model
from examples.db import sessionmanager


@asynccontextmanager
async def init_db(app: FastAPI):
    async with sessionmanager.connect() as conn:
        await conn.run_sync(Model.metadata.create_all)
        yield
        await conn.close()


app = FastAPI(lifespan=init_db)


auth_routers = FastAuthRouter(security)

app.include_router(auth_routers.get_auth_router(), tags=["Auth"])
app.include_router(
    auth_routers.get_users_router(UserRead, UserCreate, UserUpdate), tags=["Users"]
)
app.include_router(
    auth_routers.get_register_router(UserRead, UserCreate), tags=["Auth"]
)

app.include_router(auth_routers.get_verify_router(UserRead), tags=["Auth"])

app.include_router(auth_routers.get_password_router(), tags=["Auth"])

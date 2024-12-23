import os
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from httpx_oauth.clients.github import GitHubOAuth2

from examples.sqlaclhemy_full.db import sessionmanager
from examples.sqlaclhemy_full.dependency import security
from examples.sqlaclhemy_full.models import Model
from examples.sqlaclhemy_full.schema import ROUTER_SCHEMA, UserRead
from fastauth.routers import FastAuthRouter


@asynccontextmanager
async def init_db(app: FastAPI):
    async with sessionmanager.connect() as conn:
        await conn.run_sync(Model.metadata.create_all)
    yield


app = FastAPI(lifespan=init_db)
auth_router = FastAuthRouter(security)

auth_router.register_routers(app, ROUTER_SCHEMA)


@app.get("/secured-rbac", response_model=UserRead)
async def get_secured_user(
    user=Depends(security.user_required(permissions=["secured:read"])),
):
    return user


app.include_router(
    auth_router.get_oauth_router(
        GitHubOAuth2(
            os.getenv("GITHUB_CLIENT"),
            os.getenv("GITHUB_SECRET"),
        ),
        default_role=True,
    ),
)

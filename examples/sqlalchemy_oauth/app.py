from contextlib import asynccontextmanager
from fastapi import FastAPI

from .dependency import security
from .models import Model
from examples.db import sessionmanager
from fastauth.routers import FastAuthRouter
from .oauth_client import github_client


@asynccontextmanager
async def init_db(app: FastAPI):
    async with sessionmanager.connect() as conn:
        await conn.run_sync(Model.metadata.create_all)
        yield
        await conn.close()


app = FastAPI(lifespan=init_db)
auth_router = FastAuthRouter(security)

app.include_router(auth_router.get_auth_router(), tags=["Auth"])
app.include_router(auth_router.get_oauth_router(github_client))

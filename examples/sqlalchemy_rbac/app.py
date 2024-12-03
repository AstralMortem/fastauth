from fastapi import FastAPI
from fastauth.routers import FastAuthRouter
from .dependencies import security

app = FastAPI()
auth_router = FastAuthRouter(security)


app.include_router(auth_router.get_auth_router(), tags=["Auth"])

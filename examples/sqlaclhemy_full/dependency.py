from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from examples.sqlaclhemy_full.manager import AuthManager
from fastauth import FastAuth, FastAuthConfig
from fastauth.strategy import JWTStrategy

from .db import get_db
from .repository import OAuthRepository, RBACRepository, UserRepository

config = FastAuthConfig()


security = FastAuth(config)


@security.set_auth_callback
async def auth_manager(
    config: FastAuthConfig, session: AsyncSession = Depends(get_db), **kwargs
):
    return AuthManager(
        config,
        UserRepository(session),
        RBACRepository(session),
        OAuthRepository(session),
    )


@security.set_token_strategy
async def token_strategy(config: FastAuthConfig, **kwargs):
    return JWTStrategy(config)

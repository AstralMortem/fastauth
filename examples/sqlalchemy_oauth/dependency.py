from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from fastauth.backend.strategies import JWTStrategy
from fastauth.backend.transport import BearerTransport, CookieTransport
from .manager import AuthManager
from .repositories import UserRepository, OAuthRepository
from fastauth.config import FastAuthConfig
from fastauth.fastauth import FastAuth
from examples.db import get_db

config = FastAuthConfig()


def get_auth_manager(session: AsyncSession = Depends(get_db)):
    return AuthManager(
        config, UserRepository(session), oauth_repository=OAuthRepository(session)
    )


security = FastAuth(config, get_auth_manager, JWTStrategy, CookieTransport)

from sqlalchemy.ext.asyncio import AsyncSession
from fastauth.backend.strategies import JWTStrategy
from fastauth.backend.transport import BearerTransport
from fastauth.fastauth import FastAuth
from fastauth.config import FastAuthConfig
from fastapi import Depends
from examples.db import get_db
from .manager import AuthManager
from .repositories import (
    UserRepository,
    RoleRepository,
    PermissionRepository,
    OAuthRepository,
)

config = FastAuthConfig()


def get_auth_manager(session: AsyncSession = Depends(get_db)):
    return AuthManager(
        config,
        UserRepository(session),
        RoleRepository(session),
        PermissionRepository(session),
        OAuthRepository(session),
    )


security = FastAuth(config, get_auth_manager, JWTStrategy, BearerTransport)

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from examples.db import get_db
from fastauth.config import FastAuthConfig
from fastauth.fastauth import FastAuth
from .manager import AuthManager
from .repositories import UserRepository, RoleRepository, PermissionRepository
from fastauth.backend.transport import BearerTransport
from fastauth.backend.strategies import JWTStrategy

config = FastAuthConfig()


def get_auth_manager(session: AsyncSession = Depends(get_db)):
    return AuthManager(
        config,
        UserRepository(session),
        RoleRepository(session),
        PermissionRepository(session),
    )


security = FastAuth(config, get_auth_manager, JWTStrategy, BearerTransport)

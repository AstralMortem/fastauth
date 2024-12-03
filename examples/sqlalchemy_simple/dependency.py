from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from fastauth.fastauth import FastAuth
from fastauth.config import FastAuthConfig
from fastauth.backend.strategies import JWTStrategy
from fastauth.backend.transport import BearerTransport

from .manager import AuthManager
from .repository import UserRepository
from examples.db import get_db

config = FastAuthConfig()


def get_auth_manager(session: AsyncSession = Depends(get_db)):
    return AuthManager(config, UserRepository(session))


security = FastAuth(config, get_auth_manager, JWTStrategy, BearerTransport)

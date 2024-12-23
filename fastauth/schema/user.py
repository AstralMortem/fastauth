from typing import Generic, TypeVar

from fastauth.models import ID

from .base import BaseSchema


class BaseUserRead(BaseSchema, Generic[ID]):
    id: ID
    email: str
    username: str | None
    is_active: bool
    is_verified: bool


UR_S = TypeVar("UR_S", bound=BaseUserRead)


class BaseUserCreate(BaseSchema):
    email: str
    username: str | None = None
    password: str
    is_active: bool = True
    is_verified: bool = False


UC_S = TypeVar("UC_S", bound=BaseUserCreate)


class BaseUserUpdate(BaseSchema):
    email: str | None = None
    username: str | None = None


UU_S = TypeVar("UU_S", bound=BaseUserUpdate)

import uuid

from fastauth.schemas import (
    BaseUserRead,
    BaseUserUpdate,
    BaseUserCreate,
    BaseOAuthMixin,
)


class UserRead(BaseUserRead[uuid.UUID], BaseOAuthMixin):
    pass


class UserCreate(BaseUserCreate):
    pass


class UserUpdate(BaseUserUpdate):
    pass

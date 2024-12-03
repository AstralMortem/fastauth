import uuid

from fastauth.schemas import BaseUserUpdate, BaseUserCreate, BaseUserRead


class UserRead(BaseUserRead[uuid.UUID]):
    pass


class UserCreate(BaseUserCreate):
    pass


class UserUpdate(BaseUserUpdate):
    pass

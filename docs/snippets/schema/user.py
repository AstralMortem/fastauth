from fastauth.schema import BaseUserRead, BaseUserUpdate, BaseUserCreate
import uuid


class UserRead(BaseUserRead[uuid.UUID]):
    pass


class UserUpdate(BaseUserUpdate):
    pass


class UserCreate(BaseUserCreate):
    pass

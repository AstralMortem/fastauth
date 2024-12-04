import uuid
from fastauth.schemas import (
    BaseUserRead,
    BaseUserUpdate,
    BaseUserCreate,
    BaseRBACCreateMixin,
    BaseRBACMixin,
    BaseOAuthMixin,
)
from .roles import RoleRead


class UserRead(BaseUserRead[uuid.UUID], BaseOAuthMixin, BaseRBACMixin[RoleRead]):
    pass


class UserCreate(BaseUserCreate, BaseRBACCreateMixin):
    pass


class UserUpdate(BaseUserUpdate):
    pass

from pydantic import EmailStr
from .base import DTO
from fastauth.models import ID
from typing import Generic, Optional, TypeVar


class BaseUserRead(DTO, Generic[ID]):
    id: ID
    email: EmailStr
    username: Optional[str] = None
    is_active: bool
    is_verified: bool


class BaseUserCreate(DTO):
    email: EmailStr
    username: Optional[str] = None
    password: str
    is_active: bool = True
    is_verified: bool = False


class BaseUserUpdate(DTO):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    is_active: Optional[str] = None
    is_verified: Optional[str] = None


UR_DTO = TypeVar("UR_DTO", bound=BaseUserRead)
UC_DTO = TypeVar("UC_DTO", bound=BaseUserCreate)
UU_DTO = TypeVar("UU_DTO", bound=BaseUserUpdate)

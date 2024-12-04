from typing import Generic, Optional, TypeVar, List
from .base import DTO


class BasePermissionRead(DTO):
    id: int
    codename: str
    detail: Optional[dict] = None


class BasePermissionCreate(DTO):
    codename: str
    detail: Optional[dict] = None


class BasePermissionUpdate(DTO):
    codename: Optional[str] = None
    detail: Optional[dict] = None


PR_DTO = TypeVar("PR_DTO", bound=BasePermissionRead)
PC_DTO = TypeVar("PC_DTO", bound=BasePermissionCreate)
PU_DTO = TypeVar("PU_DTO", bound=BasePermissionUpdate)


class BaseRoleRead(DTO, Generic[PR_DTO]):
    id: int
    name: str
    permissions: List[PR_DTO] = []


class BaseRoleCreate(DTO):
    name: str


class BaseRoleUpdate(DTO):
    name: Optional[str] = None


RR_DTO = TypeVar("RR_DTO", bound=BaseRoleRead)
RC_DTO = TypeVar("RC_DTO", bound=BaseRoleCreate)
RU_DTO = TypeVar("RU_DTO", bound=BaseRoleUpdate)


class BaseRBACMixin(Generic[RR_DTO]):
    role: RR_DTO


class BaseRBACCreateMixin:
    role: Optional[str] = None

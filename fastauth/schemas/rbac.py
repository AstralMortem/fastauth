from typing import Generic, Optional, TypeVar, List

from .base import DTO
from fastauth.models import RP_ID, PP_ID


class BasePermissionRead(DTO, Generic[PP_ID]):
    id: PP_ID
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


class BaseRoleRead(DTO, Generic[RP_ID, PR_DTO]):
    id: RP_ID
    name: str
    permissions: List[PR_DTO] = []


class BaseRoleCreate(DTO):
    name: str


class BaseRoleUpdate(DTO):
    name: Optional[str] = None


RR_DTO = TypeVar("RR_DTO", bound=BaseRoleRead)
RC_DTO = TypeVar("RC_DTO", bound=BaseRoleCreate)
RU_DTO = TypeVar("RU_DTO", bound=BaseRoleUpdate)

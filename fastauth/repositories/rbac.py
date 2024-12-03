from abc import abstractmethod
from fastauth.models import PP_ID, RP_ID, RP, PP
from typing import Generic, Optional, Type
from fastauth.repositories.base import AbstractCRUDRepository


class AbstractRoleRepository(Generic[RP, RP_ID], AbstractCRUDRepository[RP, RP_ID]):
    model: Type[RP]


class AbstractPermissionRepository(
    Generic[PP, PP_ID], AbstractCRUDRepository[PP, PP_ID]
):
    model: Type[PP]

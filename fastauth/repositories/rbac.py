from abc import ABC
from fastauth.models import RP, PP
from typing import Generic, Type
from fastauth.repositories.base import AbstractCRUDRepository


class AbstractRoleRepository(Generic[RP], AbstractCRUDRepository[RP, int], ABC):
    model: Type[RP]


class AbstractPermissionRepository(Generic[PP], AbstractCRUDRepository[PP, int], ABC):
    model: Type[PP]

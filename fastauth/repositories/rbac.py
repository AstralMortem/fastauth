from abc import ABC, abstractmethod
from fastauth.models import RP, PP
from typing import Generic, Type
from fastauth.repositories.base import AbstractCRUDRepository


class AbstractRoleRepository(Generic[RP], AbstractCRUDRepository[RP, int], ABC):
    model: Type[RP]

    @abstractmethod
    async def get_by_name(self, role_name: str) -> RP:
        raise NotImplementedError


class AbstractPermissionRepository(Generic[PP], AbstractCRUDRepository[PP, int], ABC):
    model: Type[PP]

    @abstractmethod
    async def get_by_code(self, codename: str) -> RP:
        raise NotImplementedError

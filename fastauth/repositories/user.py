from typing import Generic, Type, Optional
from fastauth.models import ID, UP
from .base import AbstractCRUDRepository
from abc import ABC, abstractmethod


class AbstractUserRepository(Generic[UP, ID], AbstractCRUDRepository[UP, ID], ABC):
    model: Type[UP]

    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[UP]:
        raise NotImplementedError

    @abstractmethod
    async def get_by_username(self, username: str) -> Optional[UP]:
        raise NotImplementedError

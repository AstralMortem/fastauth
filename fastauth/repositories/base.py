from abc import ABC, abstractmethod
from typing import Dict, Any, Generic, Optional, List, Protocol, Type
from fastauth.models import AUTH_MODEL, ID


class AbstractCRUDRepository(Generic[AUTH_MODEL, ID], ABC):
    model: Type[AUTH_MODEL]

    @abstractmethod
    async def create(self, data: Dict[str, Any]) -> AUTH_MODEL:
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, pk: ID) -> Optional[AUTH_MODEL]:
        raise NotImplementedError

    @abstractmethod
    async def update(self, model: AUTH_MODEL, data: Dict[str, Any]) -> AUTH_MODEL:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, model: AUTH_MODEL) -> None:
        raise NotImplementedError

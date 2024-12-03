from fastauth.models import OAP, ID, UOAP
from abc import ABC, abstractmethod
from typing import Type, Generic, Any, Dict
from .base import AbstractCRUDRepository


class AbstractOAuthRepository(
    Generic[UOAP, OAP, ID], AbstractCRUDRepository[OAP, ID], ABC
):
    model: Type[OAP]
    user_model: Type[UOAP]

    @abstractmethod
    async def get_user_by_oauth(self, oauth_name: str, account_id: str) -> UOAP:
        raise NotImplementedError

    @abstractmethod
    async def add_oauth_account(self, user: UOAP, data: Dict[str, Any]) -> UOAP:
        raise NotImplementedError

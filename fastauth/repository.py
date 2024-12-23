from abc import ABC, abstractmethod
from typing import Any, Generic

from fastauth.models import ID, OAP, PP, RP, UOAP, UP

# Protocol as ORM DB adapter


class AbstractUserRepository(Generic[UP, ID], ABC):
    user_model: type[UP]

    @abstractmethod
    async def get_by_id(self, pk: ID) -> UP | None:
        raise NotImplementedError

    @abstractmethod
    async def get_by_email(self, email: str) -> UP | None:
        raise NotImplementedError

    @abstractmethod
    async def get_by_username(self, username: str) -> UP | None:
        raise NotImplementedError

    @abstractmethod
    async def get_by_fields(self, username: str, fields: list[str]) -> UP | None:
        raise NotImplementedError

    @abstractmethod
    async def get_by_field(self, value: Any, field: str) -> UP | None:
        raise NotImplementedError

    @abstractmethod
    async def create(self, data: dict[str, Any]) -> UP:
        raise NotImplementedError

    @abstractmethod
    async def update(self, user: UP, data: dict[str, Any]) -> UP:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, user: UP) -> None:
        raise NotImplementedError


class AbstractRolePermissionRepository(Generic[RP, PP], ABC):
    role_model: type[RP]
    permission_model: type[PP]

    @abstractmethod
    async def get_role(self, role_id: int) -> RP | None:
        raise NotImplementedError

    @abstractmethod
    async def get_role_by_codename(self, codename: str) -> RP | None:
        raise NotImplementedError

    @abstractmethod
    async def create_role(self, data: dict[str, Any]) -> RP:
        raise NotImplementedError

    @abstractmethod
    async def update_role(self, role: RP, data: dict[str, Any]) -> RP:
        raise NotImplementedError

    @abstractmethod
    async def delete_role(self, role: RP) -> None:
        raise NotImplementedError

    @abstractmethod
    async def list_roles(self) -> list[RP]:
        raise NotImplementedError

    @abstractmethod
    async def get_permission(self, permission_id: int) -> PP | None:
        raise NotImplementedError

    @abstractmethod
    async def get_permission_by_codename(self, codename: str) -> PP | None:
        raise NotImplementedError

    @abstractmethod
    async def create_permission(self, data: dict[str, Any]) -> PP:
        raise NotImplementedError

    @abstractmethod
    async def update_permission(self, permission: PP, data: dict[str, Any]) -> PP:
        raise NotImplementedError

    @abstractmethod
    async def delete_permission(self, permission: PP) -> None:
        raise NotImplementedError

    @abstractmethod
    async def list_permissions(self) -> list[PP]:
        raise NotImplementedError


class AbstractOAuthRepository(Generic[UOAP, OAP], ABC):
    user_model: type[UOAP]
    oauth_model: type[OAP]

    @abstractmethod
    async def get_user(self, oauth_name: str, account_id: str) -> UOAP | None:
        raise NotImplementedError

    @abstractmethod
    async def add_oauth_account(self, user: UOAP, data: dict[str, Any]) -> UOAP:
        raise NotImplementedError

    @abstractmethod
    async def update_oauth_account(
        self, user: UOAP, oauth: OAP, data: dict[str, Any]
    ) -> UOAP:
        raise NotImplementedError

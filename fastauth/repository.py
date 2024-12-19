from typing import Any, Protocol

from fastauth.models import ID, OAP, PP, RP, UP

# Protocol as ORM DB adapter


class UserRepositoryProtocol(Protocol[UP, ID]):
    async def get_by_id(self, pk: ID) -> UP | None:
        raise NotImplementedError

    async def get_by_email(self, email: str) -> UP | None:
        raise NotImplementedError

    async def get_by_username(self, username: str) -> UP | None:
        raise NotImplementedError

    async def get_by_fields(self, username: str, fields: list[str]) -> UP | None:
        raise NotImplementedError

    async def get_by_field(self, value: Any, field: str) -> UP | None:
        raise NotImplementedError

    async def create(self, data: dict[str, Any]) -> UP:
        raise NotImplementedError

    async def update(self, user: UP, data: dict[str, Any]) -> UP:
        raise NotImplementedError

    async def delete(self, user: UP) -> None:
        raise NotImplementedError


class RolePermissionRepositoryProtocol(Protocol[RP, PP]):
    async def get_permissions_by_role_name(self, role_name: str) -> list[str]:
        raise NotImplementedError


class OAuthRepositoryProtocol(Protocol[OAP]):
    pass

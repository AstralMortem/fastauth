from typing import Generic, Optional, List, Any, Dict, Protocol
from fastauth.models import ID, UP, RP, PP


# Protocol as ORM DB adapter


class UserRepositoryProtocol(Protocol[UP, ID]):
    async def get_by_id(self, pk: ID) -> Optional[UP]:
        raise NotImplementedError

    async def get_by_email(self, email: str) -> Optional[UP]:
        raise NotImplementedError

    async def get_by_username(self, username: str) -> Optional[UP]:
        raise NotImplementedError

    async def get_by_fields(self, username: str, fields: List[str]) -> Optional[UP]:
        raise NotImplementedError

    async def get_by_field(self, value: Any, field: str) -> Optional[UP]:
        raise NotImplementedError

    async def create(self, data: Dict[str, Any]) -> UP:
        raise NotImplementedError

    async def update(self, user: UP, data: Dict[str, Any]) -> UP:
        raise NotImplementedError


class RolePermissionRepositoryProtocol(Generic[RP, PP]):
    async def get_permissions_by_role_name(self, role_name: str) -> List[str]:
        raise NotImplementedError

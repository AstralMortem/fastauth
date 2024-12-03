from typing import Dict, Any, Type, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastauth.models import ID, AUTH_MODEL, UP, RP, RP_ID, PP, PP_ID
from fastauth.repositories import (
    AbstractUserRepository,
    AbstractRoleRepository,
    AbstractPermissionRepository,
)
from fastauth.repositories.base import AbstractCRUDRepository


class SQLAlchemyCRUDRepository(AbstractCRUDRepository[AUTH_MODEL, ID]):
    session: AsyncSession
    model: Type[AUTH_MODEL]

    async def get_by_id(self, pk: ID) -> Optional[AUTH_MODEL]:
        return await self.session.get(self.model, pk)

    async def create(self, data: Dict[str, Any]) -> AUTH_MODEL:
        instance = self.model(**data)
        self.session.add(instance)
        await self.session.commit()
        await self.session.refresh(instance)
        return instance

    async def update(self, model: AUTH_MODEL, data: Dict[str, Any]) -> AUTH_MODEL:
        instance = model
        for key, val in data.items():
            setattr(instance, key, val)
        await self.session.commit()
        await self.session.refresh(instance)

        return instance

    async def delete(self, model: AUTH_MODEL) -> None:
        await self.session.delete(model)

    async def list(self):
        raise NotImplementedError


class SQLAlchemyUserRepository(
    AbstractUserRepository[UP, ID], SQLAlchemyCRUDRepository[UP, ID]
):
    model: Type[UP]

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_email(self, email: str):
        qs = select(self.model).where(self.model.email == email).limit(1)
        return await self.session.scalar(qs)

    async def get_by_username(self, username: str):
        qs = select(self.model).where(self.model.username == username).limit(1)
        return await self.session.scalar(qs)


class SQLAlchemyRoleRepository(
    AbstractRoleRepository[RP, RP_ID], SQLAlchemyCRUDRepository[RP, RP_ID]
):
    model: Type[RP]

    def __init__(self, session: AsyncSession):
        self.session = session


class SQLAlchemyPermissionRepository(
    AbstractPermissionRepository[PP, PP_ID], SQLAlchemyCRUDRepository[PP, PP_ID]
):
    model: Type[PP]

    def __init__(self, session: AsyncSession):
        self.session = session


__all__ = [
    "SQLAlchemyCRUDRepository",
    "SQLAlchemyRoleRepository",
    "SQLAlchemyPermissionRepository",
    "SQLAlchemyUserRepository",
]

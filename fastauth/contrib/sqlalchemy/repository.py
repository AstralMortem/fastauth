from typing import Dict, Any, Type, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastauth.models import ID, AUTH_MODEL, UP, RP, PP, UOAP, OAP
from fastauth.repositories import (
    AbstractUserRepository,
    AbstractRoleRepository,
    AbstractPermissionRepository,
    AbstractOAuthRepository,
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
    AbstractRoleRepository[RP], SQLAlchemyCRUDRepository[RP, int]
):
    model: Type[RP]

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_name(self, role_name: str) -> RP:
        qs = select(self.model).where(self.model.name == role_name).limit(1)
        return await self.session.scalar(qs)


class SQLAlchemyPermissionRepository(
    AbstractPermissionRepository[PP], SQLAlchemyCRUDRepository[PP, int]
):
    model: Type[PP]

    def __init__(self, session: AsyncSession):
        self.session = session


class SQLAlchemyOAuthRepository(
    AbstractOAuthRepository[UOAP, OAP, ID], SQLAlchemyCRUDRepository[OAP, ID]
):
    model: Type[OAP]
    user_model: Type[UOAP]

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_user_by_oauth(self, oauth_name: str, account_id: str) -> UOAP:
        qs = (
            select(self.user_model)
            .join(self.model)
            .where(self.model.oauth_name == oauth_name)  # type: ignore
            .where(self.model.account_id == account_id)  # type: ignore
        )
        result = await self.session.execute(qs)
        return result.unique().scalar_one_or_none()

    async def add_oauth_account(self, user: UOAP, data: Dict[str, Any]) -> UOAP:
        await self.session.refresh(user)
        oauth_account = self.model(**data)
        self.session.add(oauth_account)
        user.oauth_accounts.append(oauth_account)  # type: ignore
        self.session.add(user)

        await self.session.commit()

        return user


__all__ = [
    "SQLAlchemyCRUDRepository",
    "SQLAlchemyRoleRepository",
    "SQLAlchemyPermissionRepository",
    "SQLAlchemyUserRepository",
]

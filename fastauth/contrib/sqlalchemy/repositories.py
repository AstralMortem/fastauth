from typing import Any, Generic

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from fastauth.models import ID, OAP, PP, RP, UOAP, UP
from fastauth.repositories import (
    AbstractOAuthRepository,
    AbstractRolePermissionRepository,
    AbstractUserRepository,
)


class SQLAlchemyUserRepository(AbstractUserRepository[UP, ID], Generic[UP, ID]):
    user_model: type[UP]

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, pk: ID) -> UP | None:
        return await self.session.get(self.user_model, pk)

    async def get_by_email(self, email: str) -> UP | None:
        qs = select(self.user_model).where(self.user_model.email == email).limit(1)
        return await self.session.scalar(qs)

    async def get_by_username(self, username: str) -> UP | None:
        qs = (
            select(self.user_model).where(self.user_model.username == username).limit(1)
        )
        return await self.session.scalar(qs)

    async def get_by_fields(self, fields: list[str], username: str) -> UP | None:
        qs = (
            select(self.user_model)
            .filter(
                or_(*[getattr(self.user_model, field) == username for field in fields])
            )
            .limit(1)
        )
        return await self.session.scalar(qs)

    async def get_by_field(self, field: str, value: Any) -> UP | None:
        qs = select(self.user_model).filter_by(**{field: value}).limit(1)
        return await self.session.scalar(qs)

    async def create(self, data: dict[str, Any]) -> UP:
        instance = self.user_model(**data)
        self.session.add(instance)
        await self.session.commit()
        await self.session.refresh(instance)
        return instance

    async def update(self, user: UP, data: dict[str, Any]) -> UP:
        for key, val in data.items():
            setattr(user, key, val)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def delete(self, user: UP):
        await self.session.delete(user)
        return None


class SQLAlchemyRBACRepository(
    AbstractRolePermissionRepository[RP, PP], Generic[RP, PP]
):
    role_model: type[RP]
    permission_model: type[PP]

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_role_by_id(self, role_id: int) -> RP | None:
        return await self.session.get(self.role_model, role_id)

    async def get_role_by_codename(self, codename: str) -> RP | None:
        qs = (
            select(self.role_model).where(self.role_model.codename == codename).limit(1)
        )
        return await self.session.scalar(qs)

    async def create_role(self, data: dict[str, Any]) -> RP:
        role = self.role_model(**data)
        self.session.add(role)
        await self.session.commit()
        await self.session.refresh(role)
        return role

    async def update_role(self, role: RP, data: dict[str, Any]) -> RP:
        for key, val in data.items():
            setattr(role, key, val)
        await self.session.commit()
        await self.session.refresh(role)
        return role

    async def delete_role(self, role: RP) -> None:
        await self.session.delete(role)
        return None

    async def list_roles(self) -> list[RP]:
        qs = select(self.role_model)
        return list((await self.session.scalars(qs)).unique().all())

    async def get_permission_by_id(self, permission_id: int) -> PP | None:
        return await self.session.get(self.permission_model, permission_id)

    async def get_permission_by_codename(self, codename: str) -> PP | None:
        qs = (
            select(self.permission_model)
            .where(self.permission_model.codename == codename)
            .limit(1)
        )
        return await self.session.scalar(qs)

    async def create_permission(self, data: dict[str, Any]) -> PP:
        permission = self.permission_model(**data)
        self.session.add(permission)
        await self.session.commit()
        await self.session.refresh(permission)
        return permission

    async def update_permission(self, permission: PP, data: dict[str, Any]) -> PP:
        for key, val in data.items():
            setattr(permission, key, val)
        await self.session.commit()
        await self.session.refresh(permission)
        return permission

    async def delete_permission(self, permission: PP) -> None:
        await self.session.delete(permission)
        return permission

    async def list_permissions(self) -> list[PP]:
        qs = select(self.permission_model)
        return list((await self.session.scalars(qs)).unique().all())


class SQLAlchemyOAuthRepository(AbstractOAuthRepository[UOAP, OAP], Generic[UOAP, OAP]):
    user_model: type[UOAP]
    oauth_model: type[OAP]

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_user(self, oauth_name: str, account_id: str) -> UOAP | None:
        qs = (
            select(self.user_model)
            .join(self.oauth_model)
            .where(self.oauth_model.oauth_name == oauth_name)
            .where(self.oauth_model.account_id == account_id)
        )
        res = await self.session.execute(qs)
        return res.unique().scalar_one_or_none()

    async def add_oauth_account(self, user: UOAP, data: dict[str, Any]) -> UOAP:
        oauth = self.oauth_model(**data)
        self.session.add(oauth)
        user.oauth_accounts.append(oauth)
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def update_oauth_account(
        self, user: UOAP, oauth: OAP, data: dict[str, Any]
    ) -> UOAP:
        for key, val in data.items():
            setattr(oauth, key, val)
        self.session.add(oauth)
        await self.session.commit()
        await self.session.refresh(user)
        return user


__all__ = [
    "SQLAlchemyUserRepository",
    "SQLAlchemyRBACRepository",
    "SQLAlchemyOAuthRepository",
]

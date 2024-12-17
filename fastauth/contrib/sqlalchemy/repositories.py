from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from fastauth.models import UP, ID, RP, PP
from typing import Generic, Type, Optional, List, Any, Dict


class SQLAlchemyUserRepository(Generic[UP, ID]):
    user_model: Type[UP]

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, pk: ID) -> Optional[UP]:
        return await self.session.get(self.user_model, pk)

    async def get_by_email(self, email: str) -> Optional[UP]:
        qs = select(self.user_model).where(self.user_model.email == email).limit(1)
        return await self.session.scalar(qs)

    async def get_by_username(self, username: str) -> Optional[UP]:
        qs = (
            select(self.user_model).where(self.user_model.username == username).limit(1)
        )
        return await self.session.scalar(qs)

    async def get_by_fields(self, username: str, fields: List[str]) -> Optional[UP]:
        qs = (
            select(self.user_model)
            .filter(
                or_(*[getattr(self.user_model, field) == username for field in fields])
            )
            .limit(1)
        )
        return await self.session.scalar(qs)

    async def get_by_field(self, value: Any, field: str) -> Optional[UP]:
        qs = select(self.user_model).filter_by(**{field: value}).limit(1)
        return await self.session.scalar(qs)

    async def create(self, data: Dict[str, Any]) -> UP:
        instance = self.user_model(**data)
        self.session.add(instance)
        await self.session.commit()
        await self.session.refresh(instance)
        return instance

    async def update(self, user: UP, data: Dict[str, Any]) -> UP:
        for key, val in data.items():
            setattr(user, key, val)
        await self.session.commit()
        await self.session.refresh(user)
        return user


class SQLAlchemyRBACRepository(Generic[RP, PP]):
    role_model: Type[RP]
    permission_model: Type[PP]

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_permissions_by_role_name(self, role_name: str) -> List[str]:
        qs = (
            select(self.permission_model)
            .join(self.role_model.permissions)
            .filter(self.role_model.codename == role_name)
        )
        return (await self.session.scalars(qs)).unique()


class SQLAlchemyOAuthRepository:
    pass


__all__ = [
    "SQLAlchemyUserRepository",
    "SQLAlchemyRBACRepository",
    "SQLAlchemyOAuthRepository",
]

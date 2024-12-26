from abc import ABC, abstractmethod
from typing import Any, Generic

from fastauth.models import ID, OAP, PP, RP, UOAP, UP

# Protocol as ORM DB adapter


class AbstractUserRepository(Generic[UP, ID], ABC):
    user_model: type[UP]

    @abstractmethod
    async def get_by_id(self, pk: ID) -> UP | None:
        """
        Get user by id
        :param pk: User id
        :return: User model or None
        """
        raise NotImplementedError

    @abstractmethod
    async def get_by_email(self, email: str) -> UP | None:
        """
        Get user by email
        :param email: User email
        :return User model or None
        """

        raise NotImplementedError

    @abstractmethod
    async def get_by_username(self, username: str) -> UP | None:
        """
        Get user by email
        :param username: User username
        :return User model or None
        """
        raise NotImplementedError

    @abstractmethod
    async def get_by_fields(self, fields: list[str], value: Any) -> UP | None:
        """
        Get user by multiple fields and username. Just check in cycle if user.<field> == username
        :param value: User field value
        :param fields: list of fields on user model
        :return User model or None
        """
        raise NotImplementedError

    @abstractmethod
    async def get_by_field(self, field: str, value: Any) -> UP | None:
        """
        Get user by his value in field
        :param value: User model field value
        :param field: User model field name
        :return: User model or None
        """
        raise NotImplementedError

    @abstractmethod
    async def create(self, data: dict[str, Any]) -> UP:
        """
        Create User in DB from data dict
        :param data: User model payload
        :return New User model
        """
        raise NotImplementedError

    @abstractmethod
    async def update(self, user: UP, data: dict[str, Any]) -> UP:
        """
        Update provided user model with provided data
        :param user: User model
        :param data: Data with which updates user
        :return Updated user model"""

        raise NotImplementedError

    @abstractmethod
    async def delete(self, user: UP) -> None:
        """
        Delete provided user model from db
        :param user: User model
        :return None
        """
        raise NotImplementedError


class AbstractRolePermissionRepository(Generic[RP, PP], ABC):
    role_model: type[RP]
    permission_model: type[PP]

    @abstractmethod
    async def get_role_by_id(self, role_id: int) -> RP | None:
        """
        Ger role by id
        :param role_id: INTEGER Primary key
        :return: Role model
        """

        raise NotImplementedError

    @abstractmethod
    async def get_role_by_codename(self, codename: str) -> RP | None:
        """
        Ger role by codename
        :param codename: Role codename
        :return: Role model
        """
        raise NotImplementedError

    @abstractmethod
    async def create_role(self, data: dict[str, Any]) -> RP:
        """
        Create new role in db from data dict
        :param data: Role model payload
        :return: New Role model
        """
        raise NotImplementedError

    @abstractmethod
    async def update_role(self, role: RP, data: dict[str, Any]) -> RP:
        """
        Update provided role model with provided data
        :param role: Role model
        :param data: Data with which updates role
        :return: Updated role model
        """
        raise NotImplementedError

    @abstractmethod
    async def delete_role(self, role: RP) -> None:
        """
        Delete provided role model from db
        :param role: Role model
        :return: None
        """
        raise NotImplementedError

    @abstractmethod
    async def list_roles(self) -> list[RP]:
        """
        List all roles
        :return: List of Role models
        """
        raise NotImplementedError

    @abstractmethod
    async def get_permission_by_id(self, permission_id: int) -> PP | None:
        """
        Get permission by id
        :param permission_id: INTEGER Primary key
        :return: Permission model
        """
        raise NotImplementedError

    @abstractmethod
    async def get_permission_by_codename(self, codename: str) -> PP | None:
        """
        Get permission by codename
        :param codename: Permission codename
        :return: Permission model
        """
        raise NotImplementedError

    @abstractmethod
    async def create_permission(self, data: dict[str, Any]) -> PP:
        """
        Create new permission in db from data dict
        :param data: Permission model payload
        :return: New Permission model
        """
        raise NotImplementedError

    @abstractmethod
    async def update_permission(self, permission: PP, data: dict[str, Any]) -> PP:
        """
        Update provided permission model with provided data
        :param permission: Permission model
        :param data: Data with which updates permission
        :return: Updated permission model
        """
        raise NotImplementedError

    @abstractmethod
    async def delete_permission(self, permission: PP) -> None:
        """
        Delete provided permission model from db
        :param permission: Permission model
        :return: None
        """
        raise NotImplementedError

    @abstractmethod
    async def list_permissions(self) -> list[PP]:
        """
        List all permissions
        :return: List of Permission models
        """
        raise NotImplementedError


class AbstractOAuthRepository(Generic[UOAP, OAP], ABC):
    user_model: type[UOAP]
    oauth_model: type[OAP]

    @abstractmethod
    async def get_user(self, oauth_name: str, account_id: str) -> UOAP | None:
        """
        Get user by oauth account name and id
        :param oauth_name: OAuth client name
        :param account_id: OAuthAccount model PK
        :return: User model
        """
        raise NotImplementedError

    @abstractmethod
    async def add_oauth_account(self, user: UOAP, data: dict[str, Any]) -> UOAP:
        """
        Create a new OAuth account and add it to User model
        :param user: User model
        :param data: OAuth Account data
        :return: User model
        """
        raise NotImplementedError

    @abstractmethod
    async def update_oauth_account(
        self, user: UOAP, oauth: OAP, data: dict[str, Any]
    ) -> UOAP:
        """
        Update provided OAuth account with provided data, and refresh user in DB
        :param user: User model
        :param oauth: OAuthAccount model
        :param data: Data with which updates OAuth account
        :return: Updated User model
        """
        raise NotImplementedError

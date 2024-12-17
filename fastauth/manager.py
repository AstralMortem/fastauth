from typing import Optional, List, Generic, Type
from fastauth.models import UP, ID, URPP, RP, PP
from fastauth.config import FastAuthConfig
from fastauth.repository import UserRepositoryProtocol, RolePermissionRepositoryProtocol
from fastauth import exceptions
from fastauth.schema import UC_S
from fastauth.utils.password import PasswordHelperProtocol, PasswordHelper


class BaseAuthManager(Generic[UP, ID]):
    def parse_id(self, pk: str):
        """Override this method to convert pk to ID type"""
        return pk

    def __init__(
        self,
        config: FastAuthConfig,
        user_repository: UserRepositoryProtocol[UP, ID],
        rp_protocol: Optional[RolePermissionRepositoryProtocol[RP, PP]] = None,
        password_helper: PasswordHelperProtocol = PasswordHelper(),
    ):
        self._config = config
        self.user_repo = user_repository
        self.rp_repo = rp_protocol

        self.password_helper = password_helper

    async def get_user(
        self,
        uid: str,
        is_active: Optional[bool] = None,
        is_verified: Optional[bool] = None,
    ):
        """Get user by uid and check if user is active or verified"""
        user_id: ID = self.parse_id(uid)
        user: UP = await self.user_repo.get_by_id(user_id)
        if user is None:
            raise exceptions.UserNotFound
        user = await self._check_user_verification(user, is_active, is_verified)

        return user

    async def _check_user_verification(
        self,
        user: UP,
        is_active: Optional[bool] = None,
        is_verified: Optional[bool] = None,
    ):
        """Check if user is active or verified"""
        if is_active is not None:
            if user.is_active != is_active:
                raise exceptions.UserNotFound
        if is_verified is not None:
            if user.is_verified != is_verified:
                raise exceptions.UserNotFound
        return user

    async def check_access(
        self, user: URPP, roles: List[str] = [], permissions: List[str] = []
    ):
        """Check if user has at least one role or permission to access resource"""
        if self.rp_repo is None:
            raise NotImplementedError("RolePermission repository not set")

        required_roles_set = set(roles)
        required_permissions_set = set(permissions)

        user_permissions = set(map(lambda perm: perm.codename, user.permissions))
        role_permissions = set(
            await self.rp_repo.get_permissions_by_role_name(user.role)
        )
        total_permissions = role_permissions | user_permissions

        check = bool(
            user.role.name in required_roles_set
            or total_permissions & required_permissions_set
        )
        if check is False:
            raise exceptions.AccessDenied
        return user

    async def authenticate(
        self,
        username: str,
        password: str,
        is_active: Optional[bool] = None,
        is_verified: Optional[bool] = None,
    ):
        """Return user if exists with credentials"""
        if len(self._config.USER_LOGIN_FIELDS) == 1:
            if self._config.USER_LOGIN_FIELDS[0] == "email":
                user = await self.user_repo.get_by_email(username)
            elif self._config.USER_LOGIN_FIELDS[0] == "username":
                user = await self.user_repo.get_by_username(username)
            else:
                user = None
        else:
            user = await self.user_repo.get_by_fields(
                username, self._config.USER_LOGIN_FIELDS
            )

        if user is None:
            raise exceptions.UserNotFound
        user = await self._check_user_verification(user, is_active, is_verified)

        valid, new_hash = self.password_helper.verify_and_update(
            password, user.hashed_password
        )
        if not valid:
            raise exceptions.UserNotFound

        if new_hash:
            user = await self.user_repo.update(user, {"hashed_password": new_hash})

        return user

    async def register(self, data: Type[UC_S], safe: bool = True):
        if len(self._config.USER_LOGIN_FIELDS) == 1:
            if self._config.USER_LOGIN_FIELDS[0] == "email":
                user = await self.user_repo.get_by_email(data.email)
            elif self._config.USER_LOGIN_FIELDS[0] == "username":
                user = await self.user_repo.get_by_username(data.username)
            else:
                user = None
        else:
            user = None
            for field in self._config.USER_LOGIN_FIELDS:
                user = await self.user_repo.get_by_field(getattr(data, field), field)
                if user:
                    break

        if user is not None:
            raise exceptions.UserAlreadyExists

        valid_data = data.model_dump()
        password = valid_data.get("password")
        valid_data["hashed_password"] = self.password_helper.hash(password)
        if safe:
            valid_data.pop("is_active")
            valid_data.pop("is_verified")

        user = await self.user_repo.create(valid_data)

        return user

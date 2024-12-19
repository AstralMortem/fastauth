from typing import Optional, List, Generic, Type, Union, Any, Dict
from fastapi.security import OAuth2PasswordRequestForm
from fastauth.config import FastAuthConfig
from fastauth.repository import (
    UserRepositoryProtocol,
    RolePermissionRepositoryProtocol,
    OAuthRepositoryProtocol,
)
from fastauth import exceptions
from fastauth.schema import UC_S, TokenResponse, UU_S
from fastauth.strategy.base import TokenStrategy
from fastauth.types import DependencyCallable, TokenType
from fastauth.utils.password import PasswordHelperProtocol, PasswordHelper
from fastauth.models import UP, ID, RP, PP, OAP, URPP


class BaseAuthManager(Generic[UP, ID, RP, PP, OAP]):
    def parse_id(self, pk: str):
        """Override this method to convert pk to ID type"""
        return pk

    def __init__(
        self,
        config: FastAuthConfig,
        user_repository: UserRepositoryProtocol[UP, ID],
        rp_repository: Optional[RolePermissionRepositoryProtocol[RP, PP]] = None,
        oauth_repository: Optional[OAuthRepositoryProtocol[OAP]] = None,
        password_helper: PasswordHelperProtocol = PasswordHelper(),
    ):
        self._config = config
        self.user_repo = user_repository
        self.rp_repo = rp_repository
        self.oauth_repo = oauth_repository
        self.password_helper = password_helper

    async def create_token(
        self,
        uid: str,
        token_type: TokenType,
        strategy: TokenStrategy[UP, ID],
        *,
        max_age: Optional[int] = None,
        headers: Optional[str] = None,
        extra_data: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        conf = kwargs.copy()
        if max_age:
            conf["max_age"] = max_age
        if headers:
            conf["headers"] = headers
        if extra_data:
            conf["extra_data"] = extra_data

        user = await self.get_user(uid)
        return await strategy.write_token(user, token_type, **conf)

    async def password_login(
        self, credentials: OAuth2PasswordRequestForm, strategy: TokenStrategy[UP, ID]
    ):
        if isinstance(self._config.USER_LOGIN_FIELDS, str):
            if self._config.USER_LOGIN_FIELDS == "email":
                user = await self.user_repo.get_by_email(credentials.username)
            elif self._config.USER_LOGIN_FIELDS == "username":
                user = await self.user_repo.get_by_username(credentials.username)
            else:
                user = await self.user_repo.get_by_field(
                    credentials.username, self._config.USER_LOGIN_FIELDS
                )
        else:
            user = await self.user_repo.get_by_fields(
                credentials.username, self._config.USER_LOGIN_FIELDS
            )

        if user is None:
            raise exceptions.UserNotFound

        is_valid, new_hash = self.password_helper.verify_and_update(
            credentials.password, user.hashed_password
        )
        if not is_valid:
            raise exceptions.UserNotFound
        if new_hash:
            user = self.user_repo.update(user, {"hashed_password": new_hash})

        access_token = await strategy.write_token(user, "access")
        refresh_token = (
            await strategy.write_token(user, "refresh")
            if self._config.ENABLE_REFRESH_TOKEN
            else None
        )
        return TokenResponse(access_token=access_token, refresh_token=refresh_token)

    async def check_access(
        self, user: URPP, roles: List[str] = [], permissions: List[str] = []
    ):
        """Check if user has at least one role or permission to access resource"""
        if self.rp_repo is None:
            raise NotImplementedError("RolePermission repository not set")

        required_roles_set = set(roles)
        required_permissions_set = set(permissions)

        user_permissions = set(map(lambda perm: perm.codename, user.permissions))
        role_permissions = set(map(lambda perm: perm.codename, user.role.permissions))
        total_permissions = role_permissions | user_permissions

        check = bool(
            user.role.codename in required_roles_set
            or total_permissions & required_permissions_set
        )
        if check is False:
            raise exceptions.AccessDenied
        return user

    async def register(self, data: Type[UC_S], safe: bool = True):
        if isinstance(self._config.USER_LOGIN_FIELDS, str):
            if self._config.USER_LOGIN_FIELDS == "email":
                user = await self.user_repo.get_by_email(data.email)
            elif self._config.USER_LOGIN_FIELDS == "username":
                user = await self.user_repo.get_by_username(data.username)
            else:
                user = await self.user_repo.get_by_field(
                    getattr(data, self._config.USER_LOGIN_FIELDS),
                    self._config.USER_LOGIN_FIELDS,
                )
        else:
            user = None
            for field in self._config.USER_LOGIN_FIELDS:
                user = await self.user_repo.get_by_field(getattr(data, field), field)
                if user:
                    break

        if user is not None:
            raise exceptions.UserAlreadyExists

        valid_data = data.model_dump()
        password = valid_data.pop("password")
        valid_data["hashed_password"] = self.password_helper.hash(password)
        if safe:
            valid_data.pop("is_active")
            valid_data.pop("is_verified")

        user = await self.user_repo.create(valid_data)

        return user

    # ============== USER CRUD ===========================================

    async def get_user(
        self,
        uid: str,
        is_active: Optional[bool] = None,
        is_verified: Optional[bool] = None,
    ) -> UP:
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

    async def patch_user(self, user_id: ID, data: Type[UU_S]):
        instance = await self.get_user(user_id)
        valid_data = data.model_dump()
        return self._update_user(instance, valid_data)

    async def _update_user(self, user: UP, data: Dict[str, Any]):
        return await self.user_repo.update(user, data)

    async def delete_user(self, id: ID):
        instance = await self.get_user(id)
        await self.user_repo.delete(instance)
        return None


AuthManagerDependency = DependencyCallable[
    Union[
        BaseAuthManager[UP, ID, None, None, None],
        BaseAuthManager[UP, ID, RP, PP, None],
        BaseAuthManager[UP, ID, RP, PP, OAP],
        BaseAuthManager[UP, ID, None, None, OAP],
    ]
]

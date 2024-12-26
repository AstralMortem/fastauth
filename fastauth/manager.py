from abc import abstractmethod
from typing import Any, Generic, Union

from fastapi import HTTPException, Request, Response
from fastapi.security import OAuth2PasswordRequestForm
from jwt import PyJWTError

from fastauth import exceptions
from fastauth.config import FastAuthConfig
from fastauth.models import ID, OAP, PP, RP, UOAP, UP, URPP
from fastauth.repositories import (
    AbstractOAuthRepository,
    AbstractRolePermissionRepository,
    AbstractUserRepository,
)
from fastauth.schema import PC_S, PU_S, RC_S, RU_S, UC_S, UU_S, TokenResponse
from fastauth.strategy.base import TokenStrategy
from fastauth.transport import get_login_response
from fastauth.types import DependencyCallable, TokenType
from fastauth.utils.jwt_helper import JWTHelper, TokenHelperProtocol
from fastauth.utils.password import PasswordHelper, PasswordHelperProtocol


class BaseAuthManager(Generic[UP, ID, RP, PP, OAP]):
    @abstractmethod
    def parse_id(self, pk: str):
        """Override this method to convert pk to ID type"""
        return pk  # pragma: no cover

    def __init__(
        self,
        config: FastAuthConfig,
        user_repository: AbstractUserRepository[UP, ID],
        rp_repository: AbstractRolePermissionRepository[RP, PP] | None = None,
        oauth_repository: AbstractOAuthRepository[UP, OAP] | None = None,
        *,
        password_helper: PasswordHelperProtocol | None = None,
        token_encoder: TokenHelperProtocol | None = None,
    ):
        self._config = config
        self.user_repo = user_repository
        self.rp_repo = rp_repository
        self.oauth_repo = oauth_repository
        self.password_helper = password_helper or PasswordHelper()
        self.token_encoder = token_encoder or JWTHelper(
            config.JWT_SECRET, config.JWT_ALGORITHM
        )

    async def create_token(
        self,
        uid: str,
        token_type: TokenType,
        strategy: TokenStrategy[UP, ID],
        *,
        max_age: int | None = None,
        headers: dict[str, Any] | None = None,
        extra_data: dict[str, Any] | None = None,
        **kwargs,
    ) -> str:
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
        self,
        credentials: OAuth2PasswordRequestForm,
        strategy: TokenStrategy[UP, ID],
        request: Request | None = None,
    ):
        if isinstance(self._config.USER_LOGIN_FIELDS, str):
            if self._config.USER_LOGIN_FIELDS == "email":
                user = await self.user_repo.get_by_email(credentials.username)
            elif self._config.USER_LOGIN_FIELDS == "username":
                user = await self.user_repo.get_by_username(credentials.username)
            else:
                user = await self.user_repo.get_by_field(
                    self._config.USER_LOGIN_FIELDS, credentials.username
                )
        else:
            user = await self.user_repo.get_by_fields(
                self._config.USER_LOGIN_FIELDS, credentials.username
            )

        if user is None:
            raise exceptions.UserNotFound

        is_valid, new_hash = self.password_helper.verify_and_update(
            credentials.password, user.hashed_password
        )
        if not is_valid:
            raise exceptions.UserNotFound
        if new_hash:
            user = await self.user_repo.update(user, {"hashed_password": new_hash})

        access_token = await strategy.write_token(user, "access")
        refresh_token = (
            await strategy.write_token(user, "refresh")
            if self._config.ENABLE_REFRESH_TOKEN
            else None
        )

        response = TokenResponse(access_token=access_token, refresh_token=refresh_token)
        await self.on_after_login(user, request, response)

        return response

    async def check_access(
        self,
        user: URPP,
        roles: list[str] | None = None,
        permissions: list[str] | None = None,
    ):
        """Check if user has at least one role or permission to access resource"""
        if self.rp_repo is None:
            msg = "RolePermission repository not set"
            raise NotImplementedError(msg)

        if permissions is None:
            permissions = []
        if roles is None:
            roles = []

        if len(permissions) == 0 and len(roles) == 0:
            return user

        required_roles_set = set(roles)
        required_permissions_set = set(permissions)

        user_permissions = {perm.codename for perm in user.permissions}
        role_permissions = {perm.codename for perm in user.role.permissions}
        total_permissions = role_permissions | user_permissions

        check = bool(
            user.role.codename in required_roles_set
            or total_permissions & required_permissions_set
        )
        if check is False:
            raise exceptions.AccessDenied
        return user

    async def register(
        self, data: type[UC_S], safe: bool = True, request: Request | None = None
    ):
        user = None
        if data.model_fields.get("email", None):
            user = await self.user_repo.get_by_email(data.email)
        if data.model_fields.get("username", None):
            user = await self.user_repo.get_by_username(data.username)

        if user is not None:
            raise exceptions.UserAlreadyExists

        if isinstance(self._config.USER_LOGIN_FIELDS, str):
            if data.model_fields.get(self._config.USER_LOGIN_FIELDS, None):
                user = await self.user_repo.get_by_field(
                    self._config.USER_LOGIN_FIELDS,
                    getattr(data, self._config.USER_LOGIN_FIELDS),
                )
        else:
            for field_name in self._config.USER_LOGIN_FIELDS:
                if data.model_fields.get(field_name, None):
                    user = await self.user_repo.get_by_field(
                        field_name, getattr(data, field_name)
                    )
                    if user is not None:
                        raise exceptions.UserAlreadyExists

        if user is not None:
            raise exceptions.UserAlreadyExists

        valid_data = data.model_dump()
        password = valid_data.pop("password")
        valid_data["hashed_password"] = self.password_helper.hash(password)
        if safe:
            valid_data["is_active"] = self._config.USER_DEFAULT_IS_ACTIVE
            valid_data["is_verified"] = self._config.USER_DEFAULT_IS_VERIFIED

        if role_id := valid_data.get("role_id", None) is not None:
            if safe:
                role = await self.get_role_by_codename(self._config.USER_DEFAULT_ROLE)
            else:
                role = await self.get_role(role_id)

            valid_data["role_id"] = role.id

        user = await self.user_repo.create(valid_data)

        await self.on_after_register(user, request)
        return user

    async def request_verify(self, email: str, request: Request | None = None):
        user = await self.user_repo.get_by_email(email)
        if user is None:
            raise exceptions.UserNotFound
        if not user.is_active:
            raise exceptions.UserNotFound
        if user.is_verified:
            raise HTTPException(403, "User already verified")

        payload = {
            "sub": str(user.id),
            "email": user.email,
            "aud": self._config.JWT_DEFAULT_VERIFICATION_AUDIENCE,
        }

        token = self.token_encoder.encode_token(
            payload,
            "verification",
            max_age=self._config.JWT_VERIFY_TOKEN_MAX_AGE,
        )
        await self.on_after_request_verify(user, token, request)
        return token

    async def verify(self, token: str, request: Request | None = None):
        try:
            data = self.token_encoder.decode_token(
                token, self._config.JWT_DEFAULT_VERIFICATION_AUDIENCE
            )
        except PyJWTError as e:
            raise exceptions.InvalidToken("verification") from e

        try:
            user_id = data["sub"]
            email = data["email"]
        except KeyError as e:
            raise exceptions.InvalidToken("verification") from e

        user = await self.user_repo.get_by_email(email)
        if user is None:
            raise exceptions.InvalidToken("verification")

        parsed_id = self.parse_id(user_id)
        if parsed_id != user.id:
            raise exceptions.InvalidToken("verification")

        if user.is_verified:
            raise HTTPException(403, "User already verified")

        verified_user = await self._update_user(user, {"is_verified": True})
        await self.on_after_verify(user, request)
        return verified_user

    async def forgot_password(self, email: str, request: Request | None = None):
        user = await self.user_repo.get_by_email(email)
        if user is None:
            raise exceptions.UserNotFound
        if not user.is_active:
            raise exceptions.UserNotFound

        payload = {
            "sub": str(user.id),
            "password_fgpt": self.password_helper.hash(user.hashed_password),
            "aud": self._config.JWT_DEFAULT_RESET_AUDIENCE,
        }
        token = self.token_encoder.encode_token(
            payload, "reset", max_age=self._config.JWT_RESET_TOKEN_MAX_AGE
        )
        await self.on_after_forgot_password(user, token, request)
        return token

    async def reset_password(
        self, token: str, new_password: str, request: Request | None = None
    ):
        try:
            data = self.token_encoder.decode_token(
                token, self._config.JWT_DEFAULT_RESET_AUDIENCE
            )
        except PyJWTError as e:
            raise exceptions.InvalidToken("reset") from e

        try:
            user_id = data["sub"]
            password_fingerprint = data["password_fgpt"]
        except KeyError as e:
            raise exceptions.InvalidToken("reset") from e

        user = await self.get_user(user_id, True, False)

        valid_password_fingerprint, _ = self.password_helper.verify_and_update(
            user.hashed_password, password_fingerprint
        )
        if not valid_password_fingerprint:
            raise exceptions.InvalidToken("reset")

        updated_user = await self._update_user(user, {"password": new_password})

        await self.on_after_reset_password(updated_user, request)
        return updated_user

    # ============== USER CRUD ===========================================

    async def get_user(
        self,
        uid: str,
        is_active: bool | None = None,
        is_verified: bool | None = None,
    ) -> UP:
        """Get user by uid and check if user is active or verified"""
        user_id: ID = self.parse_id(uid)
        user: UP = await self.user_repo.get_by_id(user_id)
        if user is None:
            raise exceptions.UserNotFound
        return await self._check_user_verification(user, is_active, is_verified)

    async def get_user_by_email(
        self, email: str, is_active: bool | None = None, is_verified: bool | None = None
    ):
        user: UP = await self.user_repo.get_by_email(email)
        if user is None:
            raise exceptions.UserNotFound
        return await self._check_user_verification(user, is_active, is_verified)

    async def _check_user_verification(
        self,
        user: UP,
        is_active: bool | None = None,
        is_verified: bool | None = None,
    ):
        """Check if user is active or verified"""

        is_active = is_active or self._config.USER_DEFAULT_IS_ACTIVE
        is_verified = is_verified or self._config.USER_DEFAULT_IS_VERIFIED

        if is_active is not None:
            if not user.is_active and is_active:
                raise exceptions.UserNotFound
        if is_verified is not None:
            if not user.is_verified and is_verified:
                raise exceptions.UserNotFound
        return user

    async def patch_user(
        self, user_id: ID, data: type[UU_S], request: Request | None = None
    ):
        instance = await self.get_user(user_id)
        valid_data = data.model_dump(exclude_unset=True, exclude_defaults=True)
        return await self._update_user(instance, valid_data, request)

    async def _update_user(
        self, user: UP, data: dict[str, Any], request: Request | None = None
    ):
        validated_update_dict = {}
        for field, value in data.items():
            if field == "email" and value != user.email:
                exist = await self.user_repo.get_by_email(value)
                if exist is not None:
                    raise exceptions.UserAlreadyExists
                else:
                    validated_update_dict["email"] = value
                    validated_update_dict["is_verified"] = False
            elif field == "password" and value is not None:
                validated_update_dict["hashed_password"] = self.password_helper.hash(
                    value
                )
            else:
                validated_update_dict[field] = value

        updated_user = await self.user_repo.update(user, validated_update_dict)
        await self.on_after_user_update(updated_user, validated_update_dict, request)
        return updated_user

    async def delete_user(self, user_id: ID, request: Request | None = None):
        instance = await self.get_user(user_id)
        await self.on_before_user_delete(instance, request)
        await self.user_repo.delete(instance)
        await self.on_after_user_deleted(instance, request)

    async def assign_role_to_user(self, role_id: int, user_id: str):
        role: RP = await self.get_role(role_id)
        user: URPP = await self.get_user(user_id)
        return await self._update_user(user, {"role_id": role.id})

    # ============== ROLES CRUD ======================================
    async def get_role(self, role_id: int):
        role = await self.rp_repo.get_role_by_id(role_id)
        if role is None:
            raise exceptions.RoleNotFound
        return role

    async def get_role_by_codename(self, role_name: str):
        role = await self.rp_repo.get_role_by_codename(role_name)
        if role is None:
            raise exceptions.RoleNotFound
        return role

    async def create_role(self, data: type[RC_S], request: Request | None = None):
        valid_data = data.model_dump()
        role = await self.rp_repo.create_role(valid_data)
        await self.on_after_role_created(role, valid_data, request)
        return role

    async def update_role(
        self, role_id: int, data: type[RU_S], request: Request | None = None
    ):
        role = await self.get_role(role_id)
        valid_data = data.model_dump(exclude_unset=True, exclude_defaults=True)
        role = await self.rp_repo.update_role(role, valid_data)
        await self.on_after_role_updated(role, valid_data, request)
        return role

    async def delete_role(self, role_id: int, request: Request | None = None):
        role = await self.get_role(role_id)
        await self.on_before_role_delete(role, request)
        await self.rp_repo.delete_role(role)
        await self.on_after_role_deleted(role, request)

    async def list_role(self):
        return await self.rp_repo.list_roles()

    # =========== PERMISSION CRUD ======================================

    async def get_permission(self, permission_id: int):
        perm = await self.rp_repo.get_permission_by_id(permission_id)
        if perm is None:
            raise exceptions.PermissionNotFound
        return perm

    async def get_permission_by_codename(self, permission_name: str):
        perm = await self.rp_repo.get_permission_by_codename(permission_name)
        if perm is None:
            raise exceptions.PermissionNotFound
        return perm

    async def create_permission(self, data: type[PC_S], request: Request | None = None):
        valid_data = data.model_dump()
        permission = await self.rp_repo.create_permission(valid_data)
        await self.on_after_permission_created(permission, valid_data, request)
        return permission

    async def update_permission(
        self, permission_id: int, data: type[PU_S], request: Request | None = None
    ):
        perm = await self.get_permission(permission_id)
        valid_data = data.model_dump(exclude_unset=True, exclude_defaults=True)
        permission = await self.rp_repo.update_permission(perm, valid_data)
        await self.on_after_permission_updated(permission, valid_data, request)
        return permission

    async def delete_permission(
        self, permission_id: int, request: Request | None = None
    ):
        perm = await self.get_permission(permission_id)
        await self.on_before_permission_delete(perm, request)
        await self.rp_repo.delete_permission(perm)
        await self.on_after_permission_deleted(perm, request)
        return None

    async def list_permission(self):
        return await self.rp_repo.list_permissions()

    # ================ OAUTH =====================================

    async def get_user_by_oauth_account(self, oauth_name: str, account_id: str) -> UOAP:
        user = await self.oauth_repo.get_user(oauth_name, account_id)
        if user is None:
            raise exceptions.UserNotFound
        return user

    async def oauth_callback(
        self: "BaseAuthManager[UOAP, ID]",
        oauth_name: str,
        access_token: str,
        account_id: str,
        account_email: str,
        expires_at: int | None = None,
        refresh_token: str | None = None,
        request: Request | None = None,
        *,
        associate_by_email: bool = False,
        is_verified_by_default: bool = False,
        default_role: RP | None = None,
    ):
        oauth_account_dict = {
            "oauth_name": oauth_name,
            "access_token": access_token,
            "account_id": account_id,
            "account_email": account_email,
            "expires_at": expires_at,
            "refresh_token": refresh_token,
        }

        try:
            user = await self.get_user_by_oauth_account(oauth_name, account_id)
        except Exception as e:
            try:
                # Associate account
                user = await self.get_user_by_email(account_email)
                if not associate_by_email:
                    raise exceptions.UserAlreadyExists from e
                user = await self.oauth_repo.add_oauth_account(user, oauth_account_dict)
            except exceptions.UserNotFound:
                # Create account
                password = self.password_helper.generate()
                user_dict = {
                    "email": account_email,
                    "hashed_password": self.password_helper.hash(password),
                    "is_verified": is_verified_by_default,
                }

                if default_role:
                    user_dict.update({"role_id": default_role.id})

                user = await self.user_repo.create(user_dict)
                user = await self.oauth_repo.add_oauth_account(user, oauth_account_dict)
                await self.on_after_register(user, request)
        else:
            # Update oauth
            for existing_oauth_account in user.oauth_accounts:
                if (
                    existing_oauth_account.account_id == account_id
                    and existing_oauth_account.oauth_name == oauth_name
                ):
                    user = await self.oauth_repo.update_oauth_account(
                        user, existing_oauth_account, oauth_account_dict
                    )

        return user

    async def oauth_login(
        self,
        user: UP,
        strategy: TokenStrategy[UP, ID],
        security,
        request: Request | None = None,
    ):
        access_token = await strategy.write_token(user, "access")
        refresh_token = (
            await strategy.write_token(user, "refresh")
            if self._config.ENABLE_REFRESH_TOKEN
            else None
        )
        tokens = TokenResponse(access_token=access_token, refresh_token=refresh_token)
        response = await get_login_response(security=security, tokens=tokens)
        await self.on_after_login(user, request, response)
        return response

    # =============== EVENTS ==============================================

    async def on_after_register(self, user: UP, request: Request | None = None) -> None:
        """
        Event called after user registration
        :param user: User model
        :param request: Optional fastapi request
        """
        return  # pragma: no cover

    async def on_after_user_update(
        self, user: UP, update_dict: dict[str, Any], request: Request | None = None
    ) -> None:
        """
        Event called after user update
        :param user: User model
        :param update_dict: Updated fields
        :param request: Optional fastapi request
        """
        return  # pragma: no cover

    async def on_after_request_verify(
        self, user: UP, token: str, request: Request | None = None
    ) -> None:
        """
        Event called after request verification token
        :param user: User model
        :param token: Verification token
        :param request: Optional fastapi request
        """
        return  # pragma: no cover

    async def on_after_verify(self, user: UP, request: Request | None = None) -> None:
        """
        Event called after user verification
        :param user: User model
        :param request: Optional fastapi request
        """
        return  # pragma: no cover

    async def on_after_forgot_password(
        self, user: UP, token: str, request: Request | None = None
    ) -> None:
        """
        Event called after request forgot password token
        :param user: User model
        :param token: Reset token
        :param request: Optional fastapi request
        """
        return  # pragma: no cover

    async def on_after_reset_password(
        self, user: UP, request: Request | None = None
    ) -> None:
        """
        Event called after user reset password
        :param user: User model
        :param request: Optional fastapi request
        """
        return  # pragma: no cover

    async def on_after_login(
        self,
        user: UP,
        request: Request | None = None,
        response: Response | None = None,
    ) -> None:
        """
        Event called after user login
        :param user: User model
        :param request: Optional fastapi request
        :param response: Optional fastapi response
        """
        return  # pragma: no cover

    async def on_before_user_delete(
        self, user: UP, request: Request | None = None
    ) -> None:
        """
        Event called before user deletion
        :param user: User model
        :param request: Optional fastapi request
        """
        return  # pragma: no cover

    async def on_after_user_deleted(
        self, user: UP, request: Request | None = None
    ) -> None:
        """
        Event called after user deletion
        :param user: User model
        :param request: Optional fastapi request
        """
        return  # pragma: no cover

    async def on_after_role_created(
        self, role: RP, data: dict[str, Any], request: Request | None = None
    ):
        """
        Event called after role creation
        :param role: Role model
        :param data: Role data with created to
        :param request: Optional fastapi request
        """
        return  # pragma: no cover

    async def on_after_role_updated(
        self, role: RP, data: dict[str, Any], request: Request | None = None
    ):
        """
        Event called after role update
        :param role: Role model
        :param data: Updated role data
        :param request: Optional fastapi request
        """
        return  # pragma: no cover

    async def on_after_role_deleted(self, role: RP, request: Request | None = None):
        """
        Event called after role deletion
        :param role: Role model
        :param request: Optional fastapi request
        """
        return  # pragma: no cover

    async def on_before_role_delete(self, role: RP, request: Request | None = None):
        """
        Event called before role deletion
        :param role: Role model
        :param request: Optional fastapi request
        """
        return  # pragma: no cover

    async def on_after_permission_created(
        self, permission: PP, data: dict[str, Any], request: Request | None = None
    ):
        """
        Event called after permission creation
        :param permission: permission model,
        :param data: Permission data with created to
        :param request: Optional fastapi request
        """
        return  # pragma: no cover

    async def on_after_permission_updated(
        self, permission: PP, data: dict[str, Any], request: Request | None = None
    ):
        """
        Event called after permission update
        :param permission: permission model
        :param data: Updated permission data
        :param request: Optional fastapi request
        """
        return  # pragma: no cover

    async def on_after_permission_deleted(
        self, permission: PP, request: Request | None = None
    ):
        """
        Event called after permission deletion
        :param permission: permission model
        :param request: Optional fastapi request
        """
        return  # pragma: no cover

    async def on_before_permission_delete(
        self, permission: PP, request: Request | None = None
    ):
        """
        Event called before permission deletion
        :param permission: permission model
        :param request: Optional fastapi request
        """
        return  # pragma: no cover


AuthManagerDependency = DependencyCallable[
    Union[
        BaseAuthManager[UP, ID, None, None, None],
        BaseAuthManager[UP, ID, RP, PP, None],
        BaseAuthManager[UP, ID, RP, PP, OAP],
        BaseAuthManager[UP, ID, None, None, OAP],
    ]
]

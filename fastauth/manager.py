from fastapi import HTTPException, status
from typing import Generic, Optional, Any, Union, Type, Dict
from jwt import PyJWTError
from fastauth.config import FastAuthConfig
from fastauth.repositories.oauth import AbstractOAuthRepository
from fastauth.schemas import UU_DTO, UC_DTO, RC_DTO, OAR_DTO, OAC_DTO, RU_DTO, PC_DTO
from fastauth.types import DependencyCallable
from fastauth.models import UP, RP, PP, ID, OAP, UOAP
from fastauth.repositories import (
    AbstractUserRepository,
    AbstractRoleRepository,
    AbstractPermissionRepository,
)
from fastauth.utils.jwt_helper import encode_jwt, decode_jwt
from fastauth.utils.password import PasswordHelperProtocol, PasswordHelper
from fastauth import exceptions


class BaseAuthManager(Generic[UP, ID, RP, PP, OAP]):
    user_pk_field: ID

    def __init__(
        self,
        config: FastAuthConfig,
        user_repository: AbstractUserRepository[UP, ID],
        role_repository: Optional[AbstractRoleRepository[RP]] = None,
        permission_repository: Optional[AbstractPermissionRepository[PP]] = None,
        oauth_repository: Optional[AbstractOAuthRepository[UP, OAP, ID]] = None,
        password_helper: PasswordHelperProtocol = PasswordHelper(),
    ):
        self._config = config
        self.user_repo = user_repository
        self.role_repo = role_repository
        self.perm_repo = permission_repository
        self.oauth_repo = oauth_repository
        self.password_helper = password_helper

    def parse_user_id(self, pk: Any) -> ID:
        """
        cast to user primary key from a provided value.

        :param pk: Primary key value
        :return: Parsed user primary key
        """
        return self.user_pk_field(pk)

    # ============== USER CRUD Operation =============================
    async def get_user(self, user_id: ID) -> UP:
        """
        Get user by provided user primary key.

        :param user_id: User primary key
        :return: User
        """
        instance = await self.user_repo.get_by_id(user_id)
        if instance is None:
            raise exceptions.UserNotExists()
        return instance

    async def get_user_by_email(self, email: str) -> UP:
        """
        Get user by provided email.

        :param email: User email
        :return: User
        """
        instance = await self.user_repo.get_by_email(email)
        if instance is None:
            raise exceptions.UserNotExists()
        return instance

    async def get_user_by_oauth_account(self, oath_name: str, account_id: str) -> UP:
        """
        Get user by provided OAuth account.

        :param oath_name: OAuth provider name
        :param account_id: OAuth account ID
        :return: User
        """
        user = await self.oauth_repo.get_user_by_oauth(oath_name, account_id)
        if user is None:
            raise exceptions.UserNotExists()
        return user

    async def login_user(self, username: str, password: str) -> UP:
        try:
            instance = await self.get_user_by_email(username)
        except exceptions.UserNotExists:
            # Run the hasher to mitigate timing attack
            # Inspired from Django: https://code.djangoproject.com/ticket/20760
            self.password_helper.hash(password)
            raise exceptions.UserNotExists

        check, new_hash = self.password_helper.verify_and_update(
            password, instance.hashed_password
        )
        if not check:
            raise exceptions.InvalidCredentials
        if new_hash is not None:
            instance = await self.user_repo.update(
                instance, {"hashed_password": new_hash}
            )
        return instance

    async def oauth_callback(
        self: "BaseAuthManager[UOAP, ID, RP, PP, OAP]",
        oauth_schema: Type[OAC_DTO],
        *,
        associate_by_email: bool = False,
        is_verified_by_default: bool = False,
    ) -> UOAP:
        """
        Call OAuth callback when user try to authenticate over OAuth
        :param oauth_schema: Scheme to create oauth_account in db
        :param associate_by_email: if true then try to find user by email and associate it with email
        :param is_verified_by_default: set is_verified to True or False
        :return:
        """

        oauth_account_dict = oauth_schema.model_dump()
        try:
            user = await self.get_user_by_oauth_account(
                oauth_schema.oauth_name, oauth_schema.account_id
            )
        except exceptions.UserNotExists:
            try:
                # associate account
                user = await self.get_user_by_email(oauth_schema.account_email)
                if not associate_by_email:
                    raise exceptions.UserAlreadyExists()
                user = await self.oauth_repo.add_oauth_account(user, oauth_account_dict)
            except exceptions.UserNotExists:
                # create new user and associate with oauth account
                password = self.password_helper.generate()
                user_dict = {
                    "email": oauth_schema.account_email,
                    "hashed_password": password,
                    "is_verified": is_verified_by_default,
                }
                user = await self.user_repo.create(user_dict)
                user = await self.oauth_repo.add_oauth_account(user, oauth_account_dict)
                # TODO: add on_after_register event
        else:
            for existing_oauth in user.oauth_accounts:
                if (
                    existing_oauth.account_id == oauth_schema.account_id
                    and existing_oauth.oauth_name == oauth_schema.oauth_name
                ):
                    await self.oauth_repo.update(existing_oauth, oauth_account_dict)
        await self.user_repo.session.refresh(user)
        return user

    async def oauth_associate_callback(
        self: "BaseAuthManager[UOAP, ID, RP, PP, OAP]",
        user_id: ID,
        oauth_schema: Type[OAC_DTO],
    ) -> UOAP:
        """
        Used to manually associate user with oauth account
        :param user_id:
        :param oauth_schema:
        :return:
        """

        oauth_account_dict = oauth_schema.model_dump()
        user = await self.get_user(user_id)
        user = await self.oauth_repo.add_oauth_account(user, oauth_account_dict)
        # TODO: add on_after_update event
        return user

    async def create_user(self, user_create: UC_DTO, safe: bool = True):
        """
        Check if user already exists, if not create new
        :param user_create:
        :param safe:
        :return: User
        """
        existing_user = await self.user_repo.get_by_email(user_create.email)
        if existing_user is not None:
            raise exceptions.UserAlreadyExists

        validated_data = user_create.model_dump()
        if safe:
            validated_data.pop("is_active")
            validated_data.pop("is_verified")
        if hasattr(user_create, "role"):
            role = user_create.role
            if safe:
                role = self._config.DEFAULT_USER_REGISTER_ROLE
            if role:
                role_instance = await self.get_role_by_name(role)
                role_id = role_instance.id
                validated_data["role_id"] = role_id
        validated_data.pop("role", None)

        password = validated_data.pop("password")
        validated_data["hashed_password"] = self.password_helper.hash(password)
        new_user = await self.user_repo.create(validated_data)
        # TODO: Add on_after_register event
        return new_user

    async def update_user(self, user_id: ID, user_update: UU_DTO, safe: bool = False):
        """
        Get user by id, check if user exists, then update(PATCH) user in DB and return
        :param user_id: User primary key
        :param user_update: User pydantic update schema
        :param safe: If true, don`t pop sensitive data
        :return: User
        """
        user = await self.get_user(user_id)
        validated_data = user_update.model_dump(exclude_none=True)
        if safe:
            validated_data.pop("is_active")
            validated_data.pop("is_verified")

        updated_user = await self._update(user, validated_data)
        # TODO: Add on_after_update event
        return updated_user

    async def _update(self, user: UP, update_dict: Dict[str, Any]):
        validated_update_dict = {}
        for field, value in update_dict.items():
            if field == "email" and value != user.email:
                try:
                    await self.get_user_by_email(value)
                    raise exceptions.UserAlreadyExists()
                except exceptions.UserNotExists:
                    validated_update_dict["email"] = value
                    validated_update_dict["is_verified"] = False
            elif field == "password" and value is not None:
                validated_update_dict["hashed_password"] = self.password_helper.hash(
                    value
                )
            else:
                validated_update_dict[field] = value
        return await self.user_repo.update(user, validated_update_dict)

    async def delete_user(self, user_id: ID):
        """
        Get user by id, check if user exists, then delete user from DB
        :param user_id: User primary key
        :return: None
        """
        user = await self.get_user(user_id)
        await self.user_repo.delete(user)
        # TODO: Add on_after_delete event
        return None

    # ============== ROLES CRUD Operation ======================
    async def get_role(self, role_id: int):
        """
        Ger role by id or raise RoleNotExists exception
        :param role_id:
        :return: Role
        """
        instance = await self.role_repo.get_by_id(role_id)
        if instance is None:
            raise exceptions.RoleNotExists
        return instance

    async def get_role_by_name(self, role_name: str):
        """
        Get role by role name or raise RoleNotExists exception
        :param role_name:
        :return:
        """
        instance = await self.role_repo.get_by_name(role_name)
        if instance is None:
            raise exceptions.RoleNotExists(f"{role_name} role")
        return instance

    async def create_role(self, data: Type[RC_DTO]):
        """
        Create role or raise RoleAlreadyExists
        :param data:
        :return:
        """
        try:
            await self.get_role_by_name(data.name)
            raise exceptions.RoleAlreadyExists
        except exceptions.RoleNotExists:
            valid_data = data.model_dump()
            return await self.role_repo.create(valid_data)

    async def update_role(self, role_id: int, data: Type[RU_DTO]):
        """
        Update role
        :param role_id:
        :param data:
        :return:
        """
        instance = await self.get_role(role_id)
        valid_data = data.model_dump(
            exclude_none=True, exclude_unset=True, exclude_defaults=True
        )
        return self.role_repo.update(instance, valid_data)

    async def delete_role(self, role_id: int):
        """
        Delete role
        :param role_id:
        :return:
        """
        instance = await self.get_role(role_id)
        await self.role_repo.delete(instance)

    # ============== PERMISSION CRUD Operation ======================
    async def get_permission(self, permission_id: int):
        instance = await self.perm_repo.get_by_id(permission_id)
        if instance is None:
            raise exceptions.PermissionNotExists
        return instance

    async def get_permission_by_codename(self, permission_code: str):

        instance = await self.perm_repo.get_by_code(permission_code)
        if instance is None:
            raise exceptions.PermissionNotExists(f"{permission_code} permission")
        return instance

    async def create_permission(self, data: Type[PC_DTO]):
        try:
            await self.get_permission_by_codename(data.codename)
            raise exceptions.PermissionAlreadyExists
        except exceptions.PermissionNotExists:
            valid_data = data.model_dump()
            return await self.perm_repo.create(valid_data)

    async def update_permission(self, permission_id: int, data: Type[PC_DTO]):
        instance = await self.get_permission(permission_id)
        valid_data = data.model_dump(
            exclude_none=True, exclude_unset=True, exclude_defaults=True
        )
        return self.perm_repo.update(instance, valid_data)

    async def delete_permission(self, permission_id: int):
        instance = await self.get_permission(permission_id)
        await self.perm_repo.delete(instance)


# class BaseAuthManager(Generic[UP, ID, RP, PP]):
#     user_pk_field: ID
#
#     def __init__(
#         self,
#         config: FastAuthConfig,
#         user_repository: AbstractUserRepository[UP, ID],
#         role_repository: Optional[AbstractRoleRepository[RP]] = None,
#         permission_repository: Optional[AbstractPermissionRepository[PP]] = None,
#         password_helper: PasswordHelperProtocol = PasswordHelper(),
#     ):
#         self._config = config
#         self.user_repo = user_repository
#         self.role_repo = role_repository
#         self.perm_repo = permission_repository
#         self.password_helper = password_helper
#
#     # user section
#
#     def parse_user_id(self, pk: Any) -> ID:
#         return self.user_pk_field(pk)
#
#     async def user_login(self, email: str, password: str):
#         instance = await self.user_repo.get_by_email(email)
#         if instance is None:
#             raise self.user_not_found_error()
#
#         check, new_hash = self.password_helper.verify_and_update(
#             password, instance.hashed_password
#         )
#         if not check:
#             raise self.user_not_found_error()
#         return instance
#
#     async def get_user(self, user_id: ID):
#         instance = await self.user_repo.get_by_id(user_id)
#         if not instance:
#             raise self.user_not_found_error()
#         return instance
#
#     async def get_user_by_email(self, email: str):
#         instance = await self.user_repo.get_by_email(email)
#         if not instance:
#             raise self.user_not_found_error()
#         return instance
#
#     async def update_user(self, user_id: ID, data: Type[UU_DTO]):
#         instance = await self.get_user(user_id)
#         valid_data = data.model_dump(exclude_none=True)
#         return await self.user_repo.update_user(instance, valid_data)
#
#     async def register_user(self, data: Type[UC_DTO], safe: bool = True):
#         user = await self.user_repo.get_by_email(data.email)
#         if data.username is not None and not user:
#             user = await self.user_repo.get_by_username(data.username)
#         if user:
#             raise HTTPException(
#                 status.HTTP_403_FORBIDDEN,
#                 f"User with {data.email} email already exists",
#             )
#
#         valid_data = data.model_dump(exclude_none=True)
#         password = valid_data.pop("password")
#         valid_data["hashed_password"] = self.password_helper.hash(password)
#         if safe:
#             valid_data.pop("is_active")
#             valid_data.pop("is_verified")
#
#         instance = await self.user_repo.create(valid_data)
#         return instance
#
#     async def delete_user(self, user_id: ID):
#         instance = self.get_user(user_id)
#         return await self.user_repo.delete(instance)
#
#     def user_not_found_error(self):
#         return HTTPException(status.HTTP_404_NOT_FOUND, "User not found")
#
#     # AUTH section
#
#     async def request_verify(self, email: str):
#         user = await self.get_user_by_email(email)
#         token_data = {
#             "sub": str(user.id),
#             "email": user.email,
#             "aud": self._config.JWT_USER_VERIFY_AUDIENCE,
#         }
#         token = encode_jwt(
#             token_data,
#             self._config.JWT_SECRET,
#             self._config.JWT_VERIFY_TOKEN_LIFETIME,
#             self._config.JWT_ALGORITHM,
#         )
#         # TODO: add event "after_request_verify"
#         return token
#
#     async def verify(self, token: str):
#         invalid_token = HTTPException(
#             status.HTTP_403_FORBIDDEN, "Invalid verification token"
#         )
#         try:
#             data = decode_jwt(
#                 token,
#                 self._config.JWT_SECRET,
#                 self._config.JWT_USER_VERIFY_AUDIENCE,
#                 [self._config.JWT_ALGORITHM],
#             )
#         except PyJWTError:
#             raise invalid_token
#
#         try:
#             user_id = data["sub"]
#             email = data["email"]
#         except KeyError:
#             raise invalid_token
#
#         try:
#             user = await self.get_user_by_email(email)
#         except HTTPException(404):
#             raise invalid_token
#
#         parsed_id = self.parse_user_id(user_id)
#
#         if parsed_id != user.id:
#             raise invalid_token
#         if user.is_verified:
#             raise HTTPException(status.HTTP_403_FORBIDDEN, "User already verified")
#
#         verified_user = await self.user_repo.update(user, {"is_verified": True})
#
#         return verified_user
#
#     async def forgot_password(self, email: str):
#         user = await self.get_user_by_email(email)
#
#         if not user.is_active:
#             raise HTTPException(status.HTTP_403_FORBIDDEN, "User is inactive")
#
#         token_data = {
#             "sub": str(user.id),
#             "password_fgpt": self.password_helper.hash(user.hashed_password),
#             "aud": self._config.JWT_PASSWORD_RESET_AUDIENCE,
#         }
#         token = encode_jwt(
#             token_data,
#             self._config.JWT_SECRET,
#             self._config.JWT_PASS_RESET_TOKEN_LIFETIME,
#             self._config.JWT_ALGORITHM,
#         )
#         # TODO: add event "on_reset_password_request"
#         return token
#
#     async def update_user_password(self, user: UP, new_password: str):
#         hashed_password = self.password_helper.hash(new_password)
#         return await self.user_repo.update(user, {"hashed_password": hashed_password})
#
#     async def reset_password(self, token: str, new_password: str):
#         invalid_token = HTTPException(status.HTTP_403_FORBIDDEN, "Invalid reset token")
#         try:
#             data = decode_jwt(
#                 token,
#                 self._config.JWT_SECRET,
#                 self._config.JWT_PASSWORD_RESET_AUDIENCE,
#                 [self._config.JWT_ALGORITHM],
#             )
#         except PyJWTError:
#             raise invalid_token
#
#         try:
#             user_id = data["sub"]
#             password_fingerprint = data["password_fgpt"]
#         except KeyError:
#             raise invalid_token
#
#         parsed_id = self.parse_user_id(user_id)
#
#         user = await self.get_user(parsed_id)
#         valid_password_fingerprint, _ = self.password_helper.verify_and_update(
#             user.hashed_password, password_fingerprint
#         )
#         if not valid_password_fingerprint:
#             raise invalid_token
#
#         if not user.is_active:
#             raise HTTPException(status.HTTP_403_FORBIDDEN, "User is inactive")
#
#         updated_user = await self.update_user_password(user, new_password)
#         # TODO: add after update_user_password event
#         return updated_user
#
#     def _check_role_repo(self):
#         if self.role_repo:
#             raise NotImplementedError
#
#     async def get_role(self, role_id: int):
#         self._check_role_repo()
#         instance = await self.role_repo.get_by_id(role_id)
#         if instance is None:
#             raise self.role_not_found_error()
#         return instance
#
#     async def create_role(self, data: Type[RC_DTO]):
#         self._check_role_repo()
#         valid_data = data.model_dump()
#         return self.role_repo.create(valid_data)
#
#     def role_not_found_error(self):
#         return HTTPException(status.HTTP_404_NOT_FOUND, "Role not found")
#
#
AuthManagerDependency = DependencyCallable[
    Union[
        BaseAuthManager[UP, ID, None, None, None],
        BaseAuthManager[UP, ID, RP, PP, None],
        BaseAuthManager[UP, ID, RP, PP, OAP],
        BaseAuthManager[UP, ID, None, None, OAP],
    ]
]

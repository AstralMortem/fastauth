from fastapi import HTTPException, status
from typing import Generic, Optional, Any, Union, Type
from jwt import PyJWTError
from fastauth.config import FastAuthConfig
from fastauth.schemas import UU_DTO, UC_DTO
from fastauth.types import DependencyCallable
from fastauth.models import UP, RP, PP, ID
from fastauth.repositories import (
    AbstractUserRepository,
    AbstractRoleRepository,
    AbstractPermissionRepository,
)
from fastauth.utils.jwt_helper import encode_jwt, decode_jwt
from fastauth.utils.password import PasswordHelperProtocol, PasswordHelper


class BaseAuthManager(Generic[UP, ID, RP, PP]):
    user_pk_field: ID

    def __init__(
        self,
        config: FastAuthConfig,
        user_repository: AbstractUserRepository[UP, ID],
        role_repository: Optional[AbstractRoleRepository[RP]] = None,
        permission_repository: Optional[AbstractPermissionRepository[PP]] = None,
        password_helper: PasswordHelperProtocol = PasswordHelper(),
    ):
        self._config = config
        self.user_repo = user_repository
        self.role_repo = role_repository
        self.perm_repo = permission_repository
        self.password_helper = password_helper

    def parse_user_id(self, pk: Any) -> ID:
        return self.user_pk_field(pk)

    async def user_login(self, email: str, password: str):
        instance = await self.user_repo.get_by_email(email)
        if instance is None:
            raise self.user_not_found_error()

        check, new_hash = self.password_helper.verify_and_update(
            password, instance.hashed_password
        )
        if not check:
            raise self.user_not_found_error()
        return instance

    async def get_user(self, user_id: ID):
        instance = await self.user_repo.get_by_id(user_id)
        if not instance:
            raise self.user_not_found_error()
        return instance

    async def get_user_by_email(self, email: str):
        instance = await self.user_repo.get_by_email(email)
        if not instance:
            raise self.user_not_found_error()
        return instance

    async def update_user(self, user_id: ID, data: Type[UU_DTO]):
        instance = await self.get_user(user_id)
        valid_data = data.model_dump(exclude_none=True)
        return await self.user_repo.update_user(instance, valid_data)

    async def register_user(self, data: Type[UC_DTO], safe: bool = True):
        user = await self.user_repo.get_by_email(data.email)
        if data.username is not None and not user:
            user = await self.user_repo.get_by_username(data.username)
        if user:
            raise HTTPException(
                status.HTTP_403_FORBIDDEN,
                f"User with {data.email} email already exists",
            )

        valid_data = data.model_dump(exclude_none=True)
        password = valid_data.pop("password")
        valid_data["hashed_password"] = self.password_helper.hash(password)
        if safe:
            valid_data.pop("is_active")
            valid_data.pop("is_verified")

        return await self.user_repo.create(valid_data)

    async def delete_user(self, user_id: ID):
        instance = self.get_user(user_id)
        return await self.user_repo.delete(instance)

    def user_not_found_error(self):
        return HTTPException(status.HTTP_404_NOT_FOUND, "User not found")

    async def request_verify(self, email: str):
        user = await self.get_user_by_email(email)
        token_data = {
            "sub": str(user.id),
            "email": user.email,
            "aud": self._config.JWT_USER_VERIFY_AUDIENCE,
        }
        token = encode_jwt(
            token_data,
            self._config.JWT_SECRET,
            self._config.JWT_VERIFY_TOKEN_LIFETIME,
            self._config.JWT_ALGORITHM,
        )
        # TODO: add event "after_request_verify"
        return token

    async def verify(self, token: str):
        invalid_token = HTTPException(
            status.HTTP_403_FORBIDDEN, "Invalid verification token"
        )
        try:
            data = decode_jwt(
                token,
                self._config.JWT_SECRET,
                self._config.JWT_USER_VERIFY_AUDIENCE,
                [self._config.JWT_ALGORITHM],
            )
        except PyJWTError:
            raise invalid_token

        try:
            user_id = data["sub"]
            email = data["email"]
        except KeyError:
            raise invalid_token

        try:
            user = await self.get_user_by_email(email)
        except HTTPException(404):
            raise invalid_token

        parsed_id = self.parse_user_id(user_id)

        if parsed_id != user.id:
            raise invalid_token
        if user.is_verified:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "User already verified")

        verified_user = await self.user_repo.update(user, {"is_verified": True})

        return verified_user

    async def forgot_password(self, email: str):
        user = await self.get_user_by_email(email)

        if not user.is_active:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "User is inactive")

        token_data = {
            "sub": str(user.id),
            "password_fgpt": self.password_helper.hash(user.hashed_password),
            "aud": self._config.JWT_PASSWORD_RESET_AUDIENCE,
        }
        token = encode_jwt(
            token_data,
            self._config.JWT_SECRET,
            self._config.JWT_PASS_RESET_TOKEN_LIFETIME,
            self._config.JWT_ALGORITHM,
        )
        # TODO: add event "on_reset_password_request"
        return token

    async def update_user_password(self, user: UP, new_password: str):
        hashed_password = self.password_helper.hash(new_password)
        return await self.user_repo.update(user, {"hashed_password": hashed_password})

    async def reset_password(self, token: str, new_password: str):
        invalid_token = HTTPException(status.HTTP_403_FORBIDDEN, "Invalid reset token")
        try:
            data = decode_jwt(
                token,
                self._config.JWT_SECRET,
                self._config.JWT_PASSWORD_RESET_AUDIENCE,
                [self._config.JWT_ALGORITHM],
            )
        except PyJWTError:
            raise invalid_token

        try:
            user_id = data["sub"]
            password_fingerprint = data["password_fgpt"]
        except KeyError:
            raise invalid_token

        parsed_id = self.parse_user_id(user_id)

        user = await self.get_user(parsed_id)
        valid_password_fingerprint, _ = self.password_helper.verify_and_update(
            user.hashed_password, password_fingerprint
        )
        if not valid_password_fingerprint:
            raise invalid_token

        if not user.is_active:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "User is inactive")

        updated_user = await self.update_user_password(user, new_password)
        # TODO: add after update_user_password event
        return updated_user


AuthManagerDependency = DependencyCallable[BaseAuthManager[UP, ID, RP, PP]]

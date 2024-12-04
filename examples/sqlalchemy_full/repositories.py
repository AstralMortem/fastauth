import uuid

from fastauth.contrib.sqlalchemy import repository
from .models import User, Role, Permission, OAuthAccount


class UserRepository(repository.SQLAlchemyUserRepository[User, uuid.UUID]):
    model = User


class RoleRepository(repository.SQLAlchemyRoleRepository[Role]):
    model = Role


class PermissionRepository(repository.SQLAlchemyPermissionRepository[Permission]):
    model = Permission


class OAuthRepository(
    repository.SQLAlchemyOAuthRepository[User, OAuthAccount, uuid.UUID]
):
    model = OAuthAccount
    user_model = User

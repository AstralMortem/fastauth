from fastauth.contrib.sqlalchemy import repository
from .models import User, Role, Permission
import uuid


class UserRepository(repository.SQLAlchemyUserRepository[User, uuid.UUID]):
    model = User


class RoleRepository(repository.SQLAlchemyRoleRepository[Role, int]):
    model = Role


class PermissionRepository(repository.SQLAlchemyPermissionRepository[Permission, int]):
    model = Permission

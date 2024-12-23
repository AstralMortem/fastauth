import uuid

from fastauth.contrib.sqlalchemy import repositories

from .models import OAuthAccount, Permission, Role, User


class UserRepository(repositories.SQLAlchemyUserRepository[User, uuid.UUID]):
    user_model = User


class RBACRepository(repositories.SQLAlchemyRBACRepository[Role, Permission]):
    role_model = Role
    permission_model = Permission


class OAuthRepository(repositories.SQLAlchemyOAuthRepository[User, OAuthAccount]):
    user_model = User
    oauth_model = OAuthAccount

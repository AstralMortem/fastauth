import uuid

from fastauth.contrib.sqlalchemy import repository
from .models import User, OAuthAccount


class UserRepository(repository.SQLAlchemyUserRepository[User, uuid.UUID]):
    model = User


class OAuthRepository(
    repository.SQLAlchemyOAuthRepository[User, OAuthAccount, uuid.UUID]
):
    model = OAuthAccount
    user_model = User

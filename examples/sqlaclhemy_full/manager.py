import uuid

from fastauth.manager import BaseAuthManager

from .models import OAuthAccount, Permission, Role, User


class AuthManager(BaseAuthManager[User, uuid.UUID, Role, Permission, OAuthAccount]):
    def parse_id(self, pk: str):
        return uuid.UUID(pk)

from .models import User, Role, Permission, OAuthAccount
import uuid
from fastauth.manager import BaseAuthManager


class AuthManager(BaseAuthManager[User, uuid.UUID, Role, Permission, OAuthAccount]):
    user_pk_field = uuid.UUID

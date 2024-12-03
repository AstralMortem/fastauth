from fastauth.manager import BaseAuthManager
from .models import User, OAuthAccount
import uuid


class AuthManager(BaseAuthManager[User, uuid.UUID, None, None, OAuthAccount]):
    user_pk_field = uuid.UUID

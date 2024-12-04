from fastauth.manager import BaseAuthManager
from .models import User
import uuid


class AuthManager(BaseAuthManager[User, uuid.UUID, None, None, None]):
    user_pk_field = uuid.UUID

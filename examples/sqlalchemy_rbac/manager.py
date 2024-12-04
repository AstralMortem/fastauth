import uuid
from fastauth.manager import BaseAuthManager
from .models import User, Role, Permission


class AuthManager(BaseAuthManager[User, uuid.UUID, Role, Permission, None]):
    user_pk_field = uuid.UUID

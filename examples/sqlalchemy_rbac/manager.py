import uuid
from fastauth.manager import BaseAuthManager
from .models import User, Role, Permission


class AuthManager(BaseAuthManager[User, uuid.UUID, Role, int, Permission, int]):
    user_pk_field = uuid.UUID
    role_pk_field = int
    permission_pk_field = int

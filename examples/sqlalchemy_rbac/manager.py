import uuid
from fastauth.manager import BaseAuthManager
from .models import User, Role, Permission


class AuthManager(BaseAuthManager[User, uuid.UUID, Role, Permission]):
    user_pk_field = uuid.UUID

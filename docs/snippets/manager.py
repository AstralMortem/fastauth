import uuid
from fastauth.manager import BaseAuthManager
from fastapi import Request


class AuthManager(BaseAuthManager[User, uuid.UUID, Role, Permission, OAuthAccount]):

    def parse_id(self, pk: str):
        return uuid.UUID(pk)

    async def on_after_login(self, user, request: Request | None = None):
        print(f"User {user.email} logged in")

    async def on_after_register(self, user, request: Request | None = None):
        print(f"User {user.email} registered")


async def get_auth_manager(
    config: FastAuthConfig,
    session: AsyncSession = Depends(get_db),
):
    return AuthManager(
        config,
        UserRepository(session),
        RBACRepository(session),
        OAuthRepository(session),
    )


async def get_auth_manager(
    config: FastAuthConfig,
    session: AsyncSession = Depends(get_db),
):
    return AuthManager(
        config,
        UserRepository(session),
        RBACRepository(session),
        OAuthRepository(session),
        password_helper=PasswordHelper(),
    )

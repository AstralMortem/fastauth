from typing import Any, Generic, Protocol, TypeVar

ID = TypeVar("ID")


class UserProtocol(Protocol[ID]):
    id: ID
    email: str
    username: str | None
    hashed_password: str
    is_active: bool
    is_verified: bool


UP = TypeVar("UP", bound=UserProtocol)


class PermissionProtocol(Protocol):
    id: int
    codename: str
    detail: dict[str, Any] | None


PP = TypeVar("PP", bound=PermissionProtocol)


class RoleProtocol(Protocol[PP]):
    id: int
    codename: str
    permissions: list[PP]


RP = TypeVar("RP", bound=RoleProtocol)


class RBACUserProtocol(UserProtocol[ID], Generic[ID, RP, PP]):
    role_id: int
    role: RP
    permissions: list[PP]


URPP = TypeVar("URPP", bound=RBACUserProtocol)  # user-role-permission protocol


class OAuthProtocol(Protocol[ID]):
    id: ID
    oauth_name: str
    access_token: str
    expires_at: int | None
    refresh_token: str | None
    account_id: str
    account_email: str


OAP = TypeVar("OAP", bound=OAuthProtocol)


class OAuthUserProtocol(UserProtocol[ID], Generic[ID, OAP]):
    oauth_accounts: list[OAP]


UOAP = TypeVar("UOAP", bound=OAuthUserProtocol)


class FullUserProtocol(
    RBACUserProtocol[ID, RP, PP], OAuthUserProtocol[ID, OAP], Generic[ID, RP, PP, OAP]
):
    pass


FUP = TypeVar("FUP", bound=FullUserProtocol)  # user protocol with full features


__all__ = ["ID", "UP", "RP", "PP", "URPP", "OAP", "UOAP", "FUP"]

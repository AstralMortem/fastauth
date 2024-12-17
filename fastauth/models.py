from typing import Protocol, TypeVar, Generic, Optional, List, Dict, Any

ID = TypeVar("ID")


class UserProtocol(Protocol[ID]):
    id: ID
    email: str
    username: Optional[str]
    hashed_password: str
    is_active: bool
    is_verified: bool


UP = TypeVar("UP", bound=UserProtocol)


class PermissionProtocol(Protocol):
    id: int
    codename: str
    detail: Optional[Dict[str, Any]]


PP = TypeVar("PP", bound=PermissionProtocol)


class RoleProtocol(Protocol[PP]):
    id: int
    codename: str
    permissions: List[PP]


RP = TypeVar("RP", bound=RoleProtocol)


class RBACUserProtocol(UserProtocol[ID], Generic[ID, RP, PP]):
    role_id: int
    role: RP
    permissions: List[PP]


URPP = TypeVar("URPP", bound=RBACUserProtocol)  # user-role-permission protocol


class OAuthProtocol(Protocol[ID]):
    id: ID
    oauth_name: str
    access_token: str
    expires_at: Optional[int]
    refresh_token: Optional[str]
    account_id: str
    account_email: str


OAP = TypeVar("OAP", bound=OAuthProtocol)


class OAuthUserProtocol(UserProtocol[ID], Generic[ID, OAP]):
    oauth_accounts: List[OAP]


UOAP = TypeVar("UOAP", bound=OAuthUserProtocol)


class FullUserProtocol(
    RBACUserProtocol[ID, RP, PP], OAuthUserProtocol[ID, OAP], Generic[ID, RP, PP, OAP]
):
    pass


FUP = TypeVar("FUP", bound=FullUserProtocol)  # user protocol with full features


__all__ = ["ID", "UP", "RP", "PP", "URPP", "OAP", "UOAP", "FUP"]

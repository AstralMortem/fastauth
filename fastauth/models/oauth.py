from typing import Protocol, Optional, TypeVar, List

from typing_extensions import Generic

from .user import ID, UserProtocol


class OAuthProtocol(Protocol[ID]):
    id: ID
    oauth_name: str
    access_token: str
    expires_at: Optional[int]
    refresh_token: Optional[str]
    account_id: str
    account_email: str


OAP = TypeVar("OAP", bound=OAuthProtocol)


class UserOAuthProtocol(UserProtocol[ID], Generic[ID, OAP]):
    oauth_accounts: List[OAP]


UOAP = TypeVar("UOAP", bound=UserOAuthProtocol)

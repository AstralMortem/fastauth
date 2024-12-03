from .base import BaseModel
from fastauth.models import ID
from typing import Generic, Optional, List, TypeVar


class OAuthRead(BaseModel, Generic[ID]):
    """Base OAuth scheme"""

    id: ID
    oauth_name: str
    access_token: str
    expires_at: Optional[int] = None
    refresh_token: Optional[str] = None
    account_id: str
    account_email: str


class OAuthCreate(BaseModel):
    oauth_name: str
    oauth_name: str
    access_token: str
    expires_at: Optional[int] = None
    refresh_token: Optional[str] = None
    account_id: str
    account_email: str


OAR_DTO = TypeVar("OAR_DTO", bound=OAuthRead)
OAC_DTO = TypeVar("OAC_DTO", bound=OAuthCreate)


class BaseOAuthMixin(BaseModel):
    """Adds OAuth account list to User schema"""

    oauth_accounts: List[OAuthRead] = []

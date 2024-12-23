from typing import Generic, TypeVar

from fastauth.models import ID
from fastauth.schema.base import BaseSchema


class BaseOAuthRead(BaseSchema, Generic[ID]):
    id: ID
    oauth_name: str
    access_token: str
    expires_at: int | None
    refresh_token: str | None
    account_id: str
    account_email: str


OAR_S = TypeVar("OAR_S", bound=BaseOAuthRead)


class OAuthMixin(Generic[OAR_S]):
    oauth_accounts: list[OAR_S] = []

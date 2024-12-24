import uuid
from fastauth.schema import BaseUserRead, OAuthMixin, BaseOAuthRead


class OAuthRead(BaseUserRead[uuid.UUID]):
    pass


class User(BaseUserRead[uuid.UUID], OAuthMixin[OAuthRead]):
    pass

from typing import TypeVar, Union

from .user import UserProtocol, ID, UP
from .rbac import PP, RP, RoleProtocol, PermissionProtocol
from .oauth import UserOAuthProtocol, OAuthProtocol, OAP, UOAP

AUTH_MODEL = TypeVar("AUTH_MODEL")
TYPES = ["ID", "UP", "RP", "PP", "AUTH_MODEL", "OAP", "UOAP"]
MODELS = [
    "UserProtocol",
    "RoleProtocol",
    "PermissionProtocol",
    "UserOAuthProtocol",
    "OAuthProtocol",
]

__all__ = TYPES + MODELS

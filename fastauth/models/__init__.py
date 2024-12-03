from typing import TypeVar, Union

from .user import UserProtocol, ID, UP, URBACP
from .rbac import PP, RP, RoleProtocol, PermissionProtocol

AUTH_MODEL = TypeVar("AUTH_MODEL")
TYPES = ["ID", "UP", "RP", "PP", "URBACP", "AUTH_MODEL"]
MODELS = ["UserProtocol", "RoleProtocol", "PermissionProtocol"]

__all__ = TYPES + MODELS

from typing import Protocol, TypeVar, Optional, List, Generic
from .rbac import PP, RP

ID = TypeVar("ID")


class UserProtocol(Protocol[ID]):
    id: ID
    email: str
    username: Optional[str]
    hashed_password: str
    is_active: bool
    is_verified: bool


UP = TypeVar("UP", bound=UserProtocol)

#
# class UserRBACProtocol(UserProtocol[ID], Generic[ID, RP]):
#     role_id: Optional[int] = None
#     role: Optional[RP] = None
#
#
# URBACP = TypeVar("URBACP", bound=UserRBACProtocol)

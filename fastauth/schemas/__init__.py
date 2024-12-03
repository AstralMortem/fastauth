from .token import TokenResponse, TokenPayload
from .user import (
    BaseUserRead,
    BaseUserUpdate,
    BaseUserCreate,
    UserRBACMixin,
    UU_DTO,
    UC_DTO,
    UR_DTO,
)
from .rbac import (
    BaseRoleRead,
    BaseRoleCreate,
    BaseRoleUpdate,
    BasePermissionRead,
    BasePermissionCreate,
    BasePermissionUpdate,
    PC_DTO,
    PR_DTO,
    PU_DTO,
    RR_DTO,
    RC_DTO,
    RU_DTO,
)

from .oauth import OAuthRead, BaseOAuthMixin, OAR_DTO, OAuthCreate, OAC_DTO

USER = [
    "BaseUserRead",
    "BaseUserUpdate",
    "BaseUserCreate",
    "UserRBACMixin" "UU_DTO",
    "UC_DTO",
    "UR_DTO",
]
ROLE = [
    "BaseRoleRead",
    "BaseRoleCreate",
    "BaseRoleUpdate",
    "RR_DTO",
    "RU_DTO",
    "RC_DTO",
]
PERMISSION = [
    "BasePermissionRead",
    "BasePermissionCreate",
    "BasePermissionUpdate",
    "PC_DTO",
    "PU_DTO",
    "PR_DTO",
]

OAUTH = ["OAuthRead", "BaseOAuthMixin", "OAR_DTO", "OAuthCreate", "OAC_DTO"]

TOKEN = ["TokenResponse", "TokenPayload"]

__all__ = USER + TOKEN + ROLE + PERMISSION + OAUTH

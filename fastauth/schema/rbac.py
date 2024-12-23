from typing import Generic, TypeVar

from .base import BaseSchema


class BasePermissionRead(BaseSchema):
    id: int
    codename: str


class BasePermissionCreate(BaseSchema):
    codename: str


class BasePermissionUpdate(BaseSchema):
    codename: str | None = None


PR_S = TypeVar("PR_S", bound=BasePermissionRead)
PC_S = TypeVar("PC_S", bound=BasePermissionCreate)
PU_S = TypeVar("PU_S", bound=BasePermissionUpdate)


class BaseRoleRead(BaseSchema, Generic[PR_S]):
    id: int
    codename: str
    permissions: list[PR_S]


class BaseRoleCreate(BaseSchema):
    codename: str
    permissions: list[int] = []


class BaseRoleUpdate(BaseSchema):
    codename: str | None = None
    permissions: list[int] | None = None


RR_S = TypeVar("RR_S", bound=BaseRoleRead)
RC_S = TypeVar("RC_S", bound=BaseRoleCreate)
RU_S = TypeVar("RU_S", bound=BaseRoleUpdate)


class RBACMixin(Generic[RR_S, PR_S]):
    def __init_subclass__(cls, **kwargs):
        if cls.__name__.lower().endswith("read"):
            cls.__annotations__.update(
                {"role_id": int, "role": RR_S, "permissions": list[PR_S]}
            )
        else:
            cls.__annotations__.update({"role_id": int})

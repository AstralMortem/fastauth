import uuid
from typing import Protocol, TypeVar, Union

PP_ID = TypeVar("PP_ID")


class PermissionProtocol(Protocol[PP_ID]):
    id: PP_ID
    codename: str
    detail: dict


PP = TypeVar("PP", bound=PermissionProtocol)

RP_ID = TypeVar("RP_ID")


class RoleProtocol(Protocol[RP_ID]):
    id: RP_ID
    name: str
    permissions: list[PermissionProtocol]


RP = TypeVar("RP", bound=RoleProtocol)

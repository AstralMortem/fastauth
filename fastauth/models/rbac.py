from typing import Protocol, TypeVar, Union


class PermissionProtocol(Protocol):
    id: int
    codename: str
    detail: dict


PP = TypeVar("PP", bound=PermissionProtocol)


class RoleProtocol(Protocol):
    id: int
    name: str
    permissions: list[PermissionProtocol]


RP = TypeVar("RP", bound=RoleProtocol)

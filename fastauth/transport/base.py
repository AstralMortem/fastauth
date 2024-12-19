from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from fastapi import Request, Response
from fastapi.security.base import SecurityBase

from fastauth.config import FastAuthConfig
from fastauth.schema import TokenResponse

if TYPE_CHECKING:
    from fastauth.fastauth import FastAuth


class TokenTransport(ABC):
    def __init__(self, config: FastAuthConfig):
        self._config = config

    @abstractmethod
    def schema(self, request: Request, refresh: bool = False) -> type[SecurityBase]:
        raise NotImplementedError

    @abstractmethod
    async def login_response(
        self,
        security: "FastAuth",
        content: TokenResponse,
        response: Response | None = None,
    ) -> Response:
        raise NotImplementedError

    @abstractmethod
    async def logout_response(
        self, security: "FastAuth", response: Response | None = None
    ) -> Response:
        raise NotImplementedError

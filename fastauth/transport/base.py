from abc import ABC, abstractmethod
from typing import Type, TYPE_CHECKING, Optional

from fastapi.security.base import SecurityBase
from fastauth.config import FastAuthConfig
from fastapi import Response, Request

from fastauth.schema import TokenResponse

if TYPE_CHECKING:
    from fastauth.fastauth import FastAuth


class TokenTransport(ABC):
    def __init__(self, config: FastAuthConfig):
        self._config = config

    @property
    def config(self):
        return self._config

    @abstractmethod
    def schema(self, request: Request, refresh: bool = False) -> Type[SecurityBase]:
        raise NotImplementedError

    @abstractmethod
    async def login_response(
        self,
        security: "FastAuth",
        content: TokenResponse,
        response: Optional[Response] = None,
    ) -> Response:
        raise NotImplementedError

    @abstractmethod
    async def logout_response(
        self, security: "FastAuth", response: Optional[Response] = None
    ) -> Response:
        raise NotImplementedError

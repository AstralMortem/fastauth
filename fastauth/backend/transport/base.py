from abc import ABC, abstractmethod
from typing import Optional
from fastapi.security.base import SecurityBase
from fastauth.config import FastAuthConfig
from fastapi import Response, Request


class BaseTransport(ABC):

    def __init__(self, config: FastAuthConfig):
        self._config = config

    @abstractmethod
    async def schema(self):
        raise NotImplementedError

    @abstractmethod
    async def get_login_response(
        self, access_token: str, refresh_token: Optional[str] = None
    ) -> Response:
        raise NotImplementedError

    @abstractmethod
    async def get_logout_response(self) -> Response:
        raise NotImplementedError

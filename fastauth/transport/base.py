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
        """
        Return the security schema for the token transport
        :param request: FastAPI request
        :param refresh: Flag if the token is a refresh type
        :return: SecurityBase instance
        """

        raise NotImplementedError

    @abstractmethod
    async def login_response(
        self,
        security: "FastAuth",
        content: TokenResponse,
        response: Response | None = None,
    ) -> Response:
        """
        Generate the login response
        :param security: FastAuth instance
        :param content: TokenResponse instance
        :param response: FastAPI Response instance
        :return: FastAPI Response instance
        """
        raise NotImplementedError

    @abstractmethod
    async def logout_response(
        self, security: "FastAuth", response: Response | None = None
    ) -> Response:
        """
        Generate the logout response
        :param security: FastAuth instance
        :param response: FastAPI Response instance
        :return: FastAPI Response instance
        """
        raise NotImplementedError

from abc import ABC, abstractmethod
from typing import Generic
from fastauth.models import UP
from fastauth.config import FastAuthConfig
from fastauth.schemas import TokenResponse, TokenPayload
from fastauth.types import TokenType


class BaseStrategy(ABC, Generic[UP]):

    def __init__(self, config: FastAuthConfig):
        self._config = config

    @abstractmethod
    async def read_token(self, token: str) -> TokenPayload:
        raise NotImplementedError

    @abstractmethod
    async def write_token(
        self, user: UP, type: TokenType = "access", **extra_fields
    ) -> str:
        raise NotImplementedError

    @abstractmethod
    async def destroy_token(self) -> None:
        raise NotImplementedError

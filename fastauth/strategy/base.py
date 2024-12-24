from abc import ABC, abstractmethod
from typing import Any, Generic

from fastauth.config import FastAuthConfig
from fastauth.models import ID, UP
from fastauth.types import DependencyCallable, TokenType


class TokenStrategy(Generic[UP, ID], ABC):
    def __init__(self, config: FastAuthConfig):
        self._config = config

    @abstractmethod
    async def read_token(self, token: str, **kwargs) -> dict[str, Any]:
        """
        Decode token and try fetch User model
        :param token: Token string
        :param kwargs: Extra data
        :return: Token payload dict
        """
        raise NotImplementedError

    @abstractmethod
    async def write_token(self, user: UP, token_type: TokenType, **kwargs) -> str:
        """
        Create token from User model
        :param user: User model
        :param token_type: Token type
        :param kwargs: Extra user data
        :return: Token string
        """
        raise NotImplementedError


TokenStrategyDependency = DependencyCallable[TokenStrategy[UP, ID]]

from abc import ABC, abstractmethod
from fastauth.config import FastAuthConfig
from fastauth.models import UP, ID
from typing import Generic, Any, Dict
from fastauth.types import TokenType, DependencyCallable


class TokenStrategy(Generic[UP, ID], ABC):
    def __init__(self, config: FastAuthConfig):
        self._config = config

    @abstractmethod
    async def read_token(self, token: str, **kwargs) -> Dict[str, Any]:
        """
        Decode token and try fetch User model
        :param token: Token string
        :param auth_manager: Auth Manager instance
        :param kwargs: Extra data
        :return: User model
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

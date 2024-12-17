from abc import ABC, abstractmethod
from fastauth.config import FastAuthConfig
from fastauth.schema import TokenPayload


class TokenStrategy(ABC):
    def __init__(self, config: FastAuthConfig):
        self._config = config

    @property
    def config(self):
        return self._config

    @abstractmethod
    async def read_token(self, token: str, **kwargs) -> TokenPayload:
        raise NotImplementedError

    @abstractmethod
    async def write_token(self, payload: TokenPayload, **kwargs) -> str:
        raise NotImplementedError

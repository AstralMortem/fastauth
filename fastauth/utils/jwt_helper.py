from datetime import datetime, timedelta, timezone
from typing import Any, Protocol

import jwt

from fastauth.types import StringOrSequence, TokenType


class TokenHelperProtocol(Protocol):
    def decode_token(self, token: str, *args, **kwargs) -> dict[str, Any]:
        raise NotImplementedError

    def encode_token(
        self, payload: dict[str, Any], token_type: TokenType | str, *args, **kwargs
    ) -> str:
        raise NotImplementedError


class JWTHelper:
    def __init__(self, secretkey: str, algorithm: str):
        self._secretkey = secretkey
        self._algorithm = algorithm

    def decode_token(
        self, token: str, audience: StringOrSequence | None = None, **kwargs
    ):
        return jwt.decode(
            token,
            key=self._secretkey,
            algorithms=[self._algorithm],
            audience=audience,
            **kwargs,
        )

    def encode_token(
        self,
        payload: dict[str, Any],
        token_type: TokenType | str,
        max_age: int | None = None,
        audience: StringOrSequence | None = None,
        headers: dict[str, Any] | None = None,
        **kwargs,
    ):
        payload["type"] = payload.get("type", token_type)
        payload["aud"] = payload.get("aud", audience)
        payload["iat"] = payload.get("iat", datetime.now(timezone.utc))
        payload["exp"] = payload.get(
            "exp", payload.get("iat") + timedelta(seconds=max_age)
        )
        return jwt.encode(
            payload,
            key=self._secretkey,
            algorithm=self._algorithm,
            headers=headers,
            **kwargs,
        )

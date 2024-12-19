from datetime import timedelta, timezone, datetime
from typing import Any, Dict, Optional
import jwt
from fastauth.types import StringOrSequence, TokenType


class JWT:
    def __init__(self, secretkey: str, algorithm: str):
        self._secretkey = secretkey
        self._algorithm = algorithm

    def decode_token(
        self, token: str, audience: Optional[StringOrSequence] = None, **kwargs
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
        payload: Dict[str, Any],
        token_type: TokenType,
        max_age: Optional[int] = None,
        audience: Optional[StringOrSequence] = None,
        headers: Optional[Dict[str, Any]] = None,
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

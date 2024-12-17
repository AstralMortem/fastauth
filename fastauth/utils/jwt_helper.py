from datetime import timedelta
from typing import Any, Dict, Optional
import jwt
from fastauth.config import FastAuthConfig
from fastauth.types import StringOrSequence


class JWT:
    def __init__(self, config: FastAuthConfig):
        self._config = config

    def decode_token(
        self, token: str, audience: Optional[StringOrSequence] = None, **kwargs
    ):
        return jwt.decode(
            token,
            key=self._config.JWT_SECRET,
            algorithms=[self._config.JWT_ALGORITHM],
            audience=audience,
            **kwargs,
        )

    def encode_token(
        self,
        payload: Dict[str, Any],
        max_age: Optional[int] = None,
        audience: Optional[StringOrSequence] = None,
        headers: Optional[Dict[str, Any]] = None,
        **kwargs,
    ):
        payload["aud"] = payload.get(
            "aud", audience or self._config.JWT_DEFAULT_AUDIENCE
        )
        payload["exp"] = payload.get(
            "exp", payload.get("iat") + timedelta(seconds=max_age)
        )
        return jwt.encode(
            payload,
            key=self._config.JWT_SECRET,
            algorithm=self._config.JWT_ALGORITHM,
            headers=headers,
            **kwargs,
        )

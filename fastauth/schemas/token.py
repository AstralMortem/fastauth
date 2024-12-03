from datetime import datetime, timezone
from typing import Optional, Dict, Any, List

from pydantic import BaseModel, ConfigDict


class TokenResponse(BaseModel):
    token: str
    type: str = "access"
    location: str


class BearerTokenResponse(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    type: str = "bearer"


class TokenPayload(BaseModel):
    sub: Optional[str] = None
    aud: Optional[List[str]] = None
    iat: datetime = datetime.now(timezone.utc)
    exp: Optional[datetime] = None
    type: str = "access"

    model_config = ConfigDict(extra="allow")

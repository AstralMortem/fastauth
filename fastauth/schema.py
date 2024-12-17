from typing import Optional, Generic, TypeVar
from datetime import datetime, timezone
from pydantic import BaseModel, Field, ConfigDict

from fastauth.models import ID
from fastauth.types import TokenType, StringOrSequence


class TokenPayload(BaseModel):
    sub: str
    type: TokenType = Field(default="access")
    aud: Optional[StringOrSequence] = None
    iat: Optional[datetime] = Field(default=datetime.now(timezone.utc))
    exp: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True, extra="allow")


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    type: str = "bearer"


class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class BaseUserRead(BaseSchema, Generic[ID]):
    id: ID
    email: str
    username: Optional[str]
    is_active: bool
    is_verified: bool


UR_S = TypeVar("UR_S", bound=BaseUserRead)


class BaseUserCreate(BaseSchema):
    email: str
    username: Optional[str] = None
    password: str
    is_active: bool
    is_verified: bool


UC_S = TypeVar("UC_S", bound=BaseUserCreate)


class BaseUserUpdate(BaseSchema):
    email: Optional[str] = None

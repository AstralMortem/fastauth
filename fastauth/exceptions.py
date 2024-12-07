from typing import Optional

from fastapi import HTTPException, status

from fastauth.types import TokenType


class FastAuthException(Exception):
    pass


class InvalidAuthToken(FastAuthException):
    pass


class InvalidToken(HTTPException):
    def __init__(self, token_type: TokenType = "access", extra: Optional[str] = None):
        msg = f"Invalid {token_type} token"
        if extra:
            msg += f": {extra}"
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=msg)


class UserNotExists(HTTPException):
    def __init__(self, extra: Optional[str] = None):
        msg = "User not found"
        if extra:
            msg += f": {extra}"
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=msg)


UserAlreadyExists = HTTPException(status.HTTP_403_FORBIDDEN, "User already exists")
UserAlreadyVerified = HTTPException(status.HTTP_403_FORBIDDEN, "User already verified")
UserInactive = HTTPException(status.HTTP_403_FORBIDDEN, "User is inactive")

OAuthUnavailableEmail = HTTPException(
    status.HTTP_400_BAD_REQUEST, "OAuth is not available email"
)

OAuthUserNotActive = HTTPException(status.HTTP_400_BAD_REQUEST, "User is not active")

AccessDenied = HTTPException(status.HTTP_403_FORBIDDEN, "Access denied")


class RoleNotExists(HTTPException):
    def __init__(self, extra: Optional[str] = None):
        msg = "Role not found"
        if extra:
            msg += f": {extra}"
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=msg)


RoleAlreadyExists = HTTPException(status.HTTP_403_FORBIDDEN, "Role already exists")


class PermissionNotExists(HTTPException):
    def __init__(self, extra: Optional[str] = None):
        msg = "Permission not found"
        if extra:
            msg += f": {extra}"
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=msg)


PermissionAlreadyExists = HTTPException(
    status.HTTP_403_FORBIDDEN, "Permission already exists"
)


InvalidCredentials = HTTPException(
    status.HTTP_401_UNAUTHORIZED, "Invalid credentials: Email or password"
)

from fastapi import HTTPException, status

from fastauth.types import TokenType


class TokenRequired(HTTPException):
    def __init__(self, token: TokenType | str = "access"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"{token} token is required",
        )


class MissingToken(HTTPException):
    def __init__(self, msg, headers: dict[str, str] | None = None):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=msg, headers=headers
        )


class InvalidToken(HTTPException):
    def __init__(self, msg):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=msg)


class ItemNotFound(HTTPException):
    def __init__(self, msg: str | None = None, headers: dict[str, str] | None = None):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=msg or "Item not found",
            headers=headers,
        )


class UserNotFound(ItemNotFound):
    def __init__(self):
        super().__init__("User not found")


class UserAlreadyExists(HTTPException):
    def __init__(self, msg: str | None = None):
        super().__init__(status_code=403, detail=msg or "User already exists")


# UserNotFound = ItemNotFound("User not found")
# UserAlreadyExists = HTTPException(status_code=403, detail="User already exists")


class AccessDenied(HTTPException):
    def __init__(self, msg: str | None = None):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN, detail=msg or "Access denied"
        )


class RoleNotFound(ItemNotFound):
    def __init__(self, msg: str | None = None):
        super().__init__(msg or "Role not found")


class PermissionNotFound(ItemNotFound):
    def __init__(self, msg: str | None = None):
        super().__init__(msg or "Permission not found")

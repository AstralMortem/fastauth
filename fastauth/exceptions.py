from typing import Optional, Dict
from fastapi import HTTPException, status


class TokenRequired(HTTPException):
    def __init__(self, token: str = "access"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"{token} token is required",
        )


class MissingToken(HTTPException):
    def __init__(self, msg, headers: Optional[Dict[str, str]] = None):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=msg, headers=headers
        )


class InvalidToken(HTTPException):
    def __init__(self, msg):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=msg)


class ItemNotFound(HTTPException):
    def __init__(
        self, msg: Optional[str] = None, headers: Optional[Dict[str, str]] = None
    ):
        text = "Item not found"
        if msg:
            text = msg
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND, detail=text, headers=headers
        )


UserNotFound = ItemNotFound("User not found")
UserAlreadyExists = HTTPException(status_code=403, detail="User already exists")
AccessDenied = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
)

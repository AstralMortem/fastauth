from fastapi import HTTPException, status


class TokenRequired(HTTPException):
    def __init__(self, token: str = "access"):
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

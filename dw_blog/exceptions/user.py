from uuid import UUID

from fastapi import HTTPException, status


class UserNotFound(HTTPException):
    def __init__(self, error_message: str):
        detail=error_message,
        super().__init__(
             status_code=status.HTTP_404_NOT_FOUND,
             detail=detail,
        )

from typing import List
from uuid import UUID

from fastapi import HTTPException, status


class ListException(Exception):
    def __init__(
        self,
        detail: List[HTTPException],
    ):
        self.detail = detail
        self.message = "Multiple errors occured."
        super().__init__(self.message)


class PaginationLimitSurpassed(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Pagination limit cannot be higher than 20!",
        )


class AdminStatusRequired(HTTPException):
    def __init__(self, operation: str):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"To perform {operation} you need admin status!",
        )


class AuthorStatusRequired(HTTPException):
    def __init__(self, operation: str, user_id: UUID, blog_id: UUID):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"To perform {operation} user {user_id} needs author status for blog {blog_id}!",
        )


class AdminOrAuthorRequired(HTTPException):
    def __init__(self, operation: str, entity: str):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"To perform {operation} you need either to be an admin or author of the {entity}!",
        )


class EntityUpdateFail(HTTPException):
    def __init__(self, entity_id: UUID, entity_name: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to update {entity_name} {entity_id}!",
        )


class EntityDeleteFail(HTTPException):
    def __init__(self, entity_id: UUID, entity_name: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to delete {entity_name} {entity_id}!",
        )


class EntityFailedAdd(HTTPException):
    def __init__(self, entity_name: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to add {entity_name}!",
        )

from uuid import UUID

from fastapi import HTTPException, status


class PostNotFound(HTTPException):
    def __init__(self, post_id: UUID):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id {post_id} not found!",
        )

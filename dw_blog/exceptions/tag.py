from uuid import UUID

from fastapi import HTTPException, status


class TagFailedAdd(HTTPException):
    def __init__(self, blog_id:UUID, tag_name:str):
        detail=f"Failed to add tag {tag_name} to blog {blog_id}!",
        super().__init__(
             status_code=status.HTTP_400_BAD_REQUEST,
             detail=detail,
        )
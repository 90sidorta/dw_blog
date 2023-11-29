from uuid import UUID

from fastapi import HTTPException, status


class TagFailedAdd(HTTPException):
    def __init__(self, blog_id: UUID, tag_name: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to add tag {tag_name} to blog {blog_id}!",
        )


class TagNotFound(HTTPException):
    def __init__(self, tag_id: UUID):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tag with id {tag_id} not found!",
        )


class TagUpdateFail(HTTPException):
    def __init__(self, tag_id: UUID):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to update tag {tag_id}!",
        )


class TagDeleteFail(HTTPException):
    def __init__(self, tag_id: UUID):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to delete tag {tag_id}!",
        )

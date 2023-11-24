from uuid import UUID

from fastapi import HTTPException, status


class TagFailedAdd(HTTPException):
    def __init__(self, blog_id:UUID, tag_name:str):
        detail=f"Failed to add tag {tag_name} to blog {blog_id}!",
        super().__init__(
             status_code=status.HTTP_400_BAD_REQUEST,
             detail=detail,
        )


class TagNotFound(HTTPException):
    def __init__(self, tag_id: UUID):
        detail=f"Tag with id {tag_id} not found!",
        super().__init__(
             status_code=status.HTTP_404_NOT_FOUND,
             detail=detail,
        )


class TagUpdateFail(HTTPException):
    def __init__(self):
        detail="Failed to update tag!",
        super().__init__(
             status_code=status.HTTP_400_BAD_REQUEST,
             detail=detail,
        )


class TagDeleteFail(HTTPException):
    def __init__(self):
        detail="Failed to delete tag!",
        super().__init__(
             status_code=status.HTTP_400_BAD_REQUEST,
             detail=detail,
        )

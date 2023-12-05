from uuid import UUID

from fastapi import HTTPException, status


class TagNotFound(HTTPException):
    def __init__(self, tag_id: UUID):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tag with id {tag_id} not found!",
        )


class TagListingBothFilters(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tags can either be filtered by blog or by subscriber! Can not filter by both!",
        )

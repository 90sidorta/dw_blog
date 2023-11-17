from fastapi import HTTPException, status


class BlogLimitReached(HTTPException):
    def __init__(self):
        detail="User already has 3 blogs!",
        super().__init__(
             status_code=status.HTTP_403_FORBIDDEN,
             detail=detail,
        )


class FailedBlogAdd(HTTPException):
    def __init__(self):
        detail="Failed to add blog!",
        super().__init__(
             status_code=status.HTTP_400_BAD_REQUEST,
             detail=detail,
        )


class BlogNotFound(HTTPException):
    def __init__(self):
        detail="Blog not found!",
        super().__init__(
             status_code=status.HTTP_404_NOT_FOUND,
             detail=detail,
        )

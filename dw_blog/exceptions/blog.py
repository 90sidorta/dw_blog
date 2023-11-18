from uuid import UUID

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


class AuthorsLimitReached(HTTPException):
    def __init__(self):
        detail="Blog can only have 5 authors!",
        super().__init__(
             status_code=status.HTTP_400_BAD_REQUEST,
             detail=detail,
        )


class AuthorsAddFail(HTTPException):
    def __init__(self):
        detail="Failed to add authors to the blog!",
        super().__init__(
             status_code=status.HTTP_400_BAD_REQUEST,
             detail=detail,
        )
        

class UserAlreadyAuthor(HTTPException):
    def __init__(self, author_id: UUID):
        detail=f"User {author_id} is already an author!",
        super().__init__(
             status_code=status.HTTP_403_FORBIDDEN,
             detail=detail,
        )


class NotYourBlog(HTTPException):
    def __init__(self, blog_id: UUID):
        detail=f"Blog {blog_id} does not belong to you!",
        super().__init__(
             status_code=status.HTTP_403_FORBIDDEN,
             detail=detail,
        )

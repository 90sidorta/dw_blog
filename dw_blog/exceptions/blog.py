from uuid import UUID

from fastapi import HTTPException, status


class BlogLimitReached(HTTPException):
    def __init__(self):
        detail="User already has 3 blogs!",
        super().__init__(
             status_code=status.HTTP_403_FORBIDDEN,
             detail=detail,
        )


class BlogFailedAdd(HTTPException):
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


class BlogAuthorsLimitReached(HTTPException):
    def __init__(self):
        detail="Blog can only have 5 authors!",
        super().__init__(
             status_code=status.HTTP_400_BAD_REQUEST,
             detail=detail,
        )


class BlogAuthorsAddFail(HTTPException):
    def __init__(self):
        detail="Failed to add authors to the blog!",
        super().__init__(
             status_code=status.HTTP_400_BAD_REQUEST,
             detail=detail,
        )
        

class BlogAlreadyAuthor(HTTPException):
    def __init__(self, author_id: UUID):
        detail=f"User {author_id} is already an author!",
        super().__init__(
             status_code=status.HTTP_403_FORBIDDEN,
             detail=detail,
        )


class BlogNotYours(HTTPException):
    def __init__(self, blog_id: UUID):
        detail=f"Blog {blog_id} does not belong to you!",
        super().__init__(
             status_code=status.HTTP_403_FORBIDDEN,
             detail=detail,
        )


class BlogLastAuthor(HTTPException):
    def __init__(self):
        detail="Can't delete the only author!",
        super().__init__(
             status_code=status.HTTP_400_BAD_REQUEST,
             detail=detail,
        )


class BlogDeleteAuthorFail(HTTPException):
    def __init__(self):
        detail="Can't delete the only author!",
        super().__init__(
             status_code=status.HTTP_400_BAD_REQUEST,
             detail=detail,
        )


class BlogUpdateFail(HTTPException):
    def __init__(self):
        detail="Failed to update blog!",
        super().__init__(
             status_code=status.HTTP_400_BAD_REQUEST,
             detail=detail,
        )


class BlogDeleteFail(HTTPException):
    def __init__(self):
        detail="Failed to delete blog!",
        super().__init__(
             status_code=status.HTTP_400_BAD_REQUEST,
             detail=detail,
        )

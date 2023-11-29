from uuid import UUID

from fastapi import HTTPException, status


class BlogLimitReached(HTTPException):
    def __init__(self, user_id: UUID):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"User {user_id} already has 3 blogs!",
        )


class BlogFailedAdd(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to add blog!",
        )


class BlogNotFound(HTTPException):
    def __init__(self, blog_id: UUID):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Blog {blog_id} not found!",
        )


class BlogAuthorsLimitReached(HTTPException):
    def __init__(self, blog_id: UUID):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Blog {blog_id} can only have 5 authors!",
        )


class BlogAuthorsAddFail(HTTPException):
    def __init__(self, blog_id: UUID):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to add authors to the blog {blog_id}!",
        )


class BlogAlreadyAuthor(HTTPException):
    def __init__(self, author_id: UUID):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"User {author_id} is already an author!",
        )


class BlogNotAuthor(HTTPException):
    def __init__(self, author_id: UUID, blog_id: UUID):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User {author_id} is not an author of blog {blog_id}!",
        )


class BlogNotYours(HTTPException):
    def __init__(self, blog_id: UUID):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Blog {blog_id} does not belong to you!",
        )


class BlogLastAuthor(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can't delete the only author!",
        )


class BlogDeleteAuthorFail(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to delete author!",
        )


class BlogUpdateFail(HTTPException):
    def __init__(self, blog_id: UUID):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to update blog {blog_id}!",
        )


class BlogDeleteFail(HTTPException):
    def __init__(self, blog_id: UUID):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to delete blog {blog_id}!",
        )


class BlogAlreadySubscribed(HTTPException):
    def __init__(self, blog_id: UUID):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"You already subscribed blog {blog_id}!",
        )


class BlogArchived(HTTPException):
    def __init__(self, blog_id: UUID):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Blog {blog_id} is archived!",
        )


class BlogNotSubscribed(HTTPException):
    def __init__(self, blog_id: UUID):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"You don't subscribe blog {blog_id}!",
        )


class BlogSubscribtionFail(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to subscribe this blog!",
        )


class BlogUnsubscribtionFail(HTTPException):
    def __init__(self):
        detail = ("Failed to unsubscribe this blog!",)
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
        )


class BlogAlreadyLiked(HTTPException):
    def __init__(self, blog_id: UUID):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"You already liked blog {blog_id}!",
        )


class BlogNotLiked(HTTPException):
    def __init__(self, blog_id: UUID):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"You did not like blog {blog_id}!",
        )


class BlogLikeFail(HTTPException):
    def __init__(self, blog_id: UUID):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to like blog {blog_id}!",
        )


class BlogUnlikeFail(HTTPException):
    def __init__(self, blog_id: UUID):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to unlike blog {blog_id}!",
        )

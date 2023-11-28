from uuid import UUID

from fastapi import HTTPException, status


class BlogLimitReached(HTTPException):
    def __init__(self, user_id:UUID):
        detail=f"User {user_id} already has 3 blogs!",
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
    def __init__(self, blog_id: UUID):
        detail=f"Blog {blog_id} not found!",
        super().__init__(
             status_code=status.HTTP_404_NOT_FOUND,
             detail=detail,
        )


class BlogAuthorsLimitReached(HTTPException):
    def __init__(self, blog_id: UUID):
        detail=f"Blog {blog_id} can only have 5 authors!",
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


class BlogNotAuthor(HTTPException):
    def __init__(self, author_id: UUID, blog_id: UUID):
        detail=f"User {author_id} is not an author of blog {blog_id}!",
        super().__init__(
             status_code=status.HTTP_400_BAD_REQUEST,
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
        detail="Failed to delete author!",
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


class BlogAlreadySubscribed(HTTPException):
    def __init__(self, blog_id: UUID):
        detail=f"You already subscribed blog {blog_id}!",
        super().__init__(
             status_code=status.HTTP_400_BAD_REQUEST,
             detail=detail,
        )


class BlogArchived(HTTPException):
    def __init__(self, blog_id: UUID):
        detail=f"Blog {blog_id} is archived!",
        super().__init__(
             status_code=status.HTTP_400_BAD_REQUEST,
             detail=detail,
        )


class BlogNotSubscribed(HTTPException):
    def __init__(self):
        detail="You don't subscribe this blog!",
        super().__init__(
             status_code=status.HTTP_400_BAD_REQUEST,
             detail=detail,
        )


class BlogSubscribtionFail(HTTPException):
    def __init__(self):
        detail="Failed to subscribe this blog!",
        super().__init__(
             status_code=status.HTTP_400_BAD_REQUEST,
             detail=detail,
        )


class BlogUnsubscribtionFail(HTTPException):
    def __init__(self):
        detail="Failed to unsubscribe this blog!",
        super().__init__(
             status_code=status.HTTP_400_BAD_REQUEST,
             detail=detail,
        )


class BlogAlreadyLiked(HTTPException):
    def __init__(self):
        detail="You already liked this blog!",
        super().__init__(
             status_code=status.HTTP_400_BAD_REQUEST,
             detail=detail,
        )


class BlogNotLiked(HTTPException):
    def __init__(self):
        detail="You did not like this blog!",
        super().__init__(
             status_code=status.HTTP_400_BAD_REQUEST,
             detail=detail,
        )


class BlogLikeFail(HTTPException):
    def __init__(self):
        detail="Failed to like this blog!",
        super().__init__(
             status_code=status.HTTP_400_BAD_REQUEST,
             detail=detail,
        )


class BlogUnlikeFail(HTTPException):
    def __init__(self):
        detail="Failed to unlike this blog!",
        super().__init__(
             status_code=status.HTTP_400_BAD_REQUEST,
             detail=detail,
        )

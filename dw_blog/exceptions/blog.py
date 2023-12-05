from uuid import UUID
from typing import Optional

from fastapi import HTTPException, status


class BlogLimitReached(HTTPException):
    def __init__(self, user_id: UUID):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"User {user_id} already has 3 blogs!",
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


class BlogLastAuthor(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can't delete the only author!",
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


class BlogActionFail(HTTPException):
    def __init__(self, blog_id: UUID, action: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to {action} to the blog {blog_id}!",
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


class BlogCategoryLimit(HTTPException):
    def __init__(
            self,
            blog_id: UUID,
            blog_cat_already: Optional[int] = None,
            blog_cat_add: Optional[int] = None
        ):
        if blog_cat_already and blog_cat_add:
            err_msg = f"Blog {blog_id} already has {blog_cat_already} categories! Adding {blog_cat_add} would exceed the limit of three!"
        else:
            err_msg = f"You can not delete all categories from blog {blog_id}!"
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=err_msg,
        )


class BlogAlreadyInCategory(HTTPException):
    def __init__(self, blog_id: UUID, category_id: UUID):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Blog {blog_id} already belongs to category {category_id}!",
        )


class BlogNotInCategory(HTTPException):
    def __init__(self, blog_id: UUID, category_id: UUID):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Blog {blog_id} does not belong to category {category_id}!",
        )

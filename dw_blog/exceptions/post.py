from uuid import UUID

from fastapi import HTTPException, status


class PostNotFound(HTTPException):
    def __init__(self, post_id: UUID):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id {post_id} not found!",
        )


class PostAuthorLike(HTTPException):
    def __init__(self, post_id: UUID):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Author can't like its own post {post_id}!",
        )


class PostAlreadyLiked(HTTPException):
    def __init__(self, post_id: UUID, user_id: UUID):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Post {post_id} already liked by user {user_id}!",
        )


class PostNotLiked(HTTPException):
    def __init__(self, post_id: UUID, user_id: UUID):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Post {post_id} not liked by user {user_id}!",
        )


class PostAlreadyMarked(HTTPException):
    def __init__(self, post_id: UUID, user_id: UUID):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Post {post_id} already marked as favourite by user {user_id}!",
        )


class PostNotMarked(HTTPException):
    def __init__(self, post_id: UUID, user_id: UUID):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Post {post_id} not marked as favourite by user {user_id}!",
        )


class PostTitleDuplicate(HTTPException):
    def __init__(self, title: str, blog_id: UUID):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Post with title {title} already exists for blog {blog_id}!",
        )

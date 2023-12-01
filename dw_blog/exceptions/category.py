from uuid import UUID

from fastapi import HTTPException, status


class CategoryNotFound(HTTPException):
    def __init__(self, category_id: UUID):
        super().__init__(
            status_code=status.HTTP_404_BAD_REQUEST,
            detail=f"Failed to fetch category {category_id}!",
        )


class CategoryHasBlogs(HTTPException):
    def __init__(self, category_id: UUID):
        super().__init__(
            status_code=status.HTTP_404_BAD_REQUEST,
            detail=f"Failed to fetch delete category {category_id}! It has associated blogs!",
        )

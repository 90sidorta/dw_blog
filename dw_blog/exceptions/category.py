from uuid import UUID

from fastapi import HTTPException, status


class CategoryFailedAdd(HTTPException):
    def __init__(self, category_name: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to add {category_name} category!",
        )


class CategoryNotFound(HTTPException):
    def __init__(self, category_id: UUID):
        super().__init__(
            status_code=status.HTTP_404_BAD_REQUEST,
            detail=f"Failed to fetch category {category_id}!",
        )

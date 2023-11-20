from typing import List

from fastapi import HTTPException, status


class ListException(Exception):
    def __init__(
        self,
        detail: List[HTTPException],
    ):
        self.detail = detail
        self.message = "Multiple errors occured."
        super().__init__(self.message)


class PaginationLimitSurpassed(HTTPException):
    def __init__(self):
        detail="Pagination limit cannot be higher than 20!",
        super().__init__(
             status_code=status.HTTP_400_BAD_REQUEST,
             detail=detail,
        )

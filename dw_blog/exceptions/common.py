from typing import List

from fastapi import HTTPException


class ListException(Exception):
    def __init__(
        self,
        detail: List[HTTPException],
    ):
        self.detail = detail
        self.message = "Multiple errors occured."
        super().__init__(self.message)

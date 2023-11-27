from typing import Optional
from enum import Enum

from sqlmodel import SQLModel


class UserType(str, Enum):
    admin = "admin"
    regular = "regular"


class SortOrder(str, Enum):
    ascending = "ascending"
    descending = "descending"


class ErrorModel(SQLModel):
    detail: str
    status_code: int


class Pagination(SQLModel):
    total_records: int
    limit: Optional[int] = None
    offset: Optional[int] = None


class Sort(SQLModel):
    order: SortOrder
    prop: str


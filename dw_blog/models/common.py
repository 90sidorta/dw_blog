from enum import Enum

from sqlmodel import SQLModel


class UserType(str, Enum):
    admin = "admin"
    regular = "regular"


class ErrorModel(SQLModel):
    detail: str
    status_code: int

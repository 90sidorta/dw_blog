from enum import Enum

from sqlmodel import SQLModel

from dw_blog.models.user import UserType


class TokenType(str, Enum):
    bearer = "bearer"


class Token(SQLModel):
    access_token: str
    token_type: TokenType


class AuthUser(SQLModel):
    user_id: str
    user_type: UserType

import uuid
from enum import Enum
from typing import Optional

from sqlmodel import SQLModel, Field


class UserType(str, Enum):
    author = "author"
    regular = "regular"


class UserBase(SQLModel):
    nickname: str = Field(
        min_length=3,
        max_length=100,
        unique=True,
        nullable=False,
    )
    user_type: UserType = Field(
        nullable=False,
        default=UserType.regular,
    )
    email: str = Field(
        max_length=100,
        min_length=5,
        unique=True,
        nullable=False,
        regex=r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$',
    )
    password: str = Field(nullable=False)
    description: Optional[str] = Field(
        nullable=True,
        max_length=1000,
        min_length=5,
    )


class User(UserBase, table=True):
    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        index=True
    )


class UserCreate(UserBase):
    confirm_password: str = Field(nullable=True, min_length=5, max_length=100)
    confirm_email: str = Field(
        max_length=100,
        min_length=5,
        nullable=False,
        regex=r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$',
    )


class UserRead(SQLModel):
    id: uuid.UUID
    nickname: str
    user_type: UserType
    description: Optional[str]


class UserUpdate(SQLModel):
    user_type: Optional[UserType]
    description: Optional[str] = Field(
        nullable=True,
        max_length=1000,
        min_length=5,
    ) 
    new_email: Optional[str] = Field(
        max_length=100,
        min_length=5,
        unique=True,
        nullable=True,
        regex=r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$',
    )
    confirm_email: Optional[str] = Field(
        max_length=100,
        min_length=5,
        nullable=True,
        regex=r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$',
    )
    new_password: Optional[str] = Field(nullable=True)
    confirm_password: Optional[str] = Field(nullable=True, min_length=5, max_length=100)


class UserdDelete(SQLModel):
    id: uuid.UUID

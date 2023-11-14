import uuid
from typing import Optional, List

from sqlmodel import SQLModel, Field, Relationship

from dw_blog.models.common import UserType
from dw_blog.models.blog import BlogAuthors, Blog


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
    blogs: Optional[List[Blog]] = Relationship(
        back_populates="authors",
        link_model=BlogAuthors,
    )


class UserCreate(UserBase):
    confirm_password: str = Field(nullable=True, min_length=5, max_length=100)
    confirm_email: str = Field(
        max_length=100,
        min_length=5,
        nullable=False,
        regex=r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$',
    )

    class Config:
        anystr_strip_whitespace = True
        schema_extra = {
            "example": {
                "nickname": "crazy_user_2137",
                "user_type": UserType.regular,
                "password": "testtest2!",
                "confirm_password": "testtest2!",
                "email": "crazy_user_2137@test.com",
                "confirm_email": "crazy_user_2137@test.com",
                "description": "Very descriptive description",
            }
        }


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
    class Config:
        anystr_strip_whitespace = True
        schema_extra = {
            "example": {
                "user_type": UserType.regular,
                "new_email": "testtest22!",
                "confirm_password": "testtest22!",
                "new_email": "crazy1_user_2137@test.com",
                "confirm_email": "crazy1_user_2137@test.com",
                "description": "Very descriptive description1",
            }
        }


class UserdDelete(SQLModel):
    user_id: uuid.UUID

import uuid
from datetime import datetime
from typing import List, Optional
from enum import Enum

from sqlmodel import Field, SQLModel

from dw_blog.schemas.common import Pagination, Sort


class SortCategoryBy(str, Enum):
    name = "name"
    date_created = "date_created"
    most_blogs = "most_blogs"
    blogs_with_most_likes = "blogs_with_most_likes"


class CategoryBase(SQLModel):
    name: str = Field(
        min_length=3,
        max_length=500,
        unique=True,
        nullable=False,
    )
    date_created: datetime = Field(default_factory=datetime.utcnow)
    date_modified: datetime = Field(default_factory=datetime.utcnow)
    approved: bool = Field(default=False, nullable=False)


class CategoryCreate(SQLModel):
    name: str = Field(
        min_length=3,
        max_length=500,
        nullable=False,
    )


class CategoryBlogRead(SQLModel):
    blog_id: Optional[uuid.UUID]
    blog_name: Optional[str]


class CategoryRead(SQLModel):
    id: uuid.UUID
    name: str
    date_created: datetime
    date_modified: datetime
    approved: bool
    blogs: Optional[List[CategoryBlogRead]]


class CategoryReadList(SQLModel):
    id: uuid.UUID
    name: str
    approved: bool
    blogs_count: int
    blogs: Optional[List[CategoryBlogRead]]
    date_created: datetime
    date_modified: datetime


class ReadCategoriesPagination(SQLModel):
    data: List[CategoryReadList]
    pagination: Pagination
    sort: Sort


class CategoryUpdate(CategoryCreate):
    approved: Optional[bool] 
    name: Optional[str] = Field(
        min_length=3,
        max_length=500,
        nullable=True,
    )


class CategoryDelete(CategoryRead):
    id: uuid.UUID

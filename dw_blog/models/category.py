import uuid
from datetime import datetime
from typing import List, Optional
from enum import Enum

from sqlmodel import Field, Relationship, SQLModel

from dw_blog.models.common import Pagination, Sort


class SortCategoryBy(str, Enum):
    name = "name"
    date_created = "date_created"
    most_blogs = "most_blogs"
    blogs_with_most_likes = "blogs_with_most_likes"


class CategoryBlogs(SQLModel, table=True):
    __tablename__ = "categoryblogs"
    category_id: uuid.UUID = Field(foreign_key="category.id", primary_key=True)
    blog_id: uuid.UUID = Field(foreign_key="blog.id", primary_key=True)


# class CategoryFavourite(SQLModel, table=True):
#     category_id: uuid.UUID = Field(foreign_key="category.id", primary_key=True)
#     user_id: uuid.UUID = Field(foreign_key="user.id", primary_key=True)


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


class Category(CategoryBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    blogs: List["Blog"] = Relationship(
        back_populates="categories",
        link_model=CategoryBlogs,
    )
    # favouriters: Optional[List["User"]] = Relationship(
    #     back_populates="categories",
    #     link_model=CategoryFavourite,
    # )


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
    name: Optional[str]


class CategoryDelete(CategoryRead):
    id: uuid.UUID

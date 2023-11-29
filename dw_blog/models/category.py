import uuid
from datetime import datetime
from typing import List

from sqlmodel import Field, Relationship, SQLModel


class CategoryBlogs(SQLModel, table=True):
    category_id: uuid.UUID = Field(foreign_key="tag.id", primary_key=True)
    blog_id: uuid.UUID = Field(foreign_key="post.id", primary_key=True)


class CategoryBase(SQLModel):
    name: str = Field(
        min_length=3,
        max_length=500,
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


class CategoryCreate(SQLModel):
    name: str = Field(
        min_length=3,
        max_length=500,
        nullable=False,
    )


class CategoryRead(CategoryBase):
    id: uuid.UUID


class CategoryUpdate(CategoryCreate):
    approved: bool


class CategoryDelete(CategoryRead):
    id: uuid.UUID

import uuid
from typing import List

from sqlmodel import Field, Relationship, SQLModel

from dw_blog.schemas.category import CategoryBase


class CategoryBlogs(SQLModel, table=True):
    __tablename__ = "categoryblogs"
    category_id: uuid.UUID = Field(foreign_key="category.id", primary_key=True)
    blog_id: uuid.UUID = Field(foreign_key="blog.id", primary_key=True)


# class CategoryFavourite(SQLModel, table=True):
#     category_id: uuid.UUID = Field(foreign_key="category.id", primary_key=True)
#     user_id: uuid.UUID = Field(foreign_key="user.id", primary_key=True)


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

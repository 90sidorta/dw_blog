import uuid
from typing import List

from sqlmodel import Field, Relationship, SQLModel

from dw_blog.models.category import Category, CategoryBlogs
from dw_blog.schemas.blog import BlogBase


class BlogAuthors(SQLModel, table=True):
    blog_id: uuid.UUID = Field(foreign_key="blog.id", primary_key=True)
    author_id: uuid.UUID = Field(foreign_key="user.id", primary_key=True)


class BlogLikes(SQLModel, table=True):
    blog_id: uuid.UUID = Field(foreign_key="blog.id", primary_key=True)
    liker_id: uuid.UUID = Field(foreign_key="user.id", primary_key=True)


class BlogSubscribers(SQLModel, table=True):
    blog_id: uuid.UUID = Field(foreign_key="blog.id", primary_key=True)
    subscriber_id: uuid.UUID = Field(foreign_key="user.id", primary_key=True)


class Blog(BlogBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    authors: List["User"] = Relationship(
        back_populates="blogs",
        link_model=BlogAuthors,
    )
    likers: List["User"] = Relationship(
        back_populates="liked_blogs",
        link_model=BlogLikes,
    )
    subscribers: List["User"] = Relationship(
        back_populates="subscribed_blogs",
        link_model=BlogSubscribers,
    )
    categories: List[Category] = Relationship(
        back_populates="blogs",
        link_model=CategoryBlogs,
    )
    tags: List["Tag"] = Relationship(back_populates="blog")

import uuid
from typing import List, Optional

from sqlmodel import Field, Relationship, String, Column, SQLModel, CheckConstraint
from sqlalchemy import UniqueConstraint
from sqlalchemy.dialects.postgresql import ARRAY

from dw_blog.schemas.post import PostBase
from dw_blog.models.tag import Tag, TagPosts
from dw_blog.models.blog import Blog


class PostAuthors(SQLModel, table=True):
    post_id: uuid.UUID = Field(foreign_key="post.id", primary_key=True)
    author_id: uuid.UUID = Field(foreign_key="user.id", primary_key=True)


class Post(PostBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    notes: Optional[List[str]] = Field(
        default=None,
        sa_column=Column(
            ARRAY(String(1500)),
            CheckConstraint('array_length(notes, 1) <= 5'),
        )
    )
    bibliography: Optional[List[str]] = Field(
        default=None,
        sa_column=Column(
            ARRAY(String(3500)),
            CheckConstraint('array_length(bibliography, 1) <= 5'),
        )
    )
    comments: Optional[List["Comment"]] = Relationship(back_populates="post")
    tags: List[Tag] = Relationship(
        back_populates="posts",
        link_model=TagPosts,
    )
    authors: List["User"] = Relationship(
        back_populates="posts",
        link_model=PostAuthors,
    )
    # images: Optional[List["Image"]] = Relationship(back_populates="post")
    blog_id: uuid.UUID = Field(
        default=None,
        foreign_key="blog.id",
    )
    blog: Blog = Relationship(back_populates="posts")

    __table_args__ = (
        UniqueConstraint('title', 'blog_id', name='_blog_post_title_uc'),
    )

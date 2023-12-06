import uuid
from typing import List, Optional

from sqlmodel import Field, Relationship, SQLModel

from dw_blog.schemas.tag import TagBase
from dw_blog.models.blog import Blog


class TagSubscribers(SQLModel, table=True):
    tag_id: uuid.UUID = Field(foreign_key="tag.id", primary_key=True)
    subscriber_id: uuid.UUID = Field(foreign_key="user.id", primary_key=True)


class TagPosts(SQLModel, table=True):
    tag_id: uuid.UUID = Field(foreign_key="tag.id", primary_key=True)
    post_id: uuid.UUID = Field(foreign_key="post.id", primary_key=True)


class Tag(TagBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    blog_id: uuid.UUID = Field(
        default=None,
        foreign_key="blog.id",
    )
    posts: Optional[List["Post"]] = Relationship(
        back_populates="tags",
        link_model=TagPosts,
    )
    blog: Blog = Relationship(back_populates="tags")
    subscribers: Optional[List["User"]] = Relationship(
        back_populates="subscribed_tags",
        link_model=TagSubscribers,
    )

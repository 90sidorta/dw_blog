import uuid
from datetime import datetime
from typing import List, Optional
from enum import Enum

from sqlmodel import Field, Relationship, SQLModel

from dw_blog.models.blog import Blog
from dw_blog.models.common import Pagination, Sort


class SortTagBy(str, Enum):
    most_subscribers = "most_subscribers"
    date_created = "date_created"


class TagSubscribers(SQLModel, table=True):
    tag_id: uuid.UUID = Field(foreign_key="tag.id", primary_key=True)
    subscriber_id: uuid.UUID = Field(foreign_key="user.id", primary_key=True)


class TagPosts(SQLModel, table=True):
    tag_id: uuid.UUID = Field(foreign_key="tag.id", primary_key=True)
    post_id: uuid.UUID = Field(foreign_key="post.id", primary_key=True)


class TagBase(SQLModel):
    name: str = Field(
        min_length=3,
        max_length=500,
        nullable=False,
    )
    date_created: datetime = Field(default_factory=datetime.utcnow)
    date_modified: datetime = Field(default_factory=datetime.utcnow)


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


class TagReadList(SQLModel):
    id: uuid.UUID
    name: str
    subscription_count: int
    blog_id: uuid.UUID
    date_created: datetime
    date_modified: datetime


class ReadTagsPagination(SQLModel):
    data: List[TagReadList]
    pagination: Pagination
    sort: Sort


class TagCreate(SQLModel):
    blog_id: uuid.UUID
    name: str = Field(
        min_length=3,
        max_length=500,
        nullable=False,
        regex=r"#\w+",
    )


class TagRead(TagBase):
    id: uuid.UUID
    blog_id: uuid.UUID
    blog_name: str


class TagUpdate(TagCreate):
    name: str = Field(
        min_length=3,
        max_length=500,
        nullable=False,
        regex=r"#\w+",
    )

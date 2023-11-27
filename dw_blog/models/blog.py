import uuid
from typing import List, Optional
from datetime import datetime
from enum import Enum

from sqlmodel import SQLModel, Field, Relationship

from dw_blog.models.common import Sort, Pagination


class SortBlogBy(str, Enum):
    name = "name"
    date_created = "date_created"


class BlogAuthors(SQLModel, table=True):
    blog_id: uuid.UUID = Field(foreign_key="blog.id", primary_key=True)
    author_id: uuid.UUID = Field(foreign_key="user.id", primary_key=True)


class BlogLikes(SQLModel, table=True):
    blog_id: uuid.UUID = Field(foreign_key="blog.id", primary_key=True)
    liker_id: uuid.UUID = Field(foreign_key="user.id", primary_key=True)


class BlogSubscribers(SQLModel, table=True):
    blog_id: uuid.UUID = Field(foreign_key="blog.id", primary_key=True)
    subscriber_id: uuid.UUID = Field(foreign_key="user.id", primary_key=True)


class BlogBase(SQLModel):
    name: str = Field(
        min_length=3,
        max_length=500,
        nullable=False,
    )
    archived: bool = Field(default=False)
    date_created: datetime = Field(default_factory=datetime.utcnow)
    date_modified: datetime = Field(default_factory=datetime.utcnow)


class Blog(BlogBase, table=True):
    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        index=True
    )
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
    tags: List["Tag"] = Relationship(back_populates="blog")


class BlogCreate(SQLModel):
    name: str = Field(
        min_length=3,
        max_length=500,
        nullable=False,
    )


class BlogUpdate(SQLModel):
    name: Optional[str] = Field(
        min_length=3,
        max_length=500,
        nullable=True,
    )
    archived: Optional[bool] = False


class BlogAuthor(SQLModel):
    author_id: Optional[uuid.UUID]
    nickname: Optional[str]


class BlogLiker(SQLModel):
    liker_id: Optional[uuid.UUID]
    nickname: Optional[str]


class BlogSubscriber(SQLModel):
    subscriber_id: Optional[uuid.UUID]
    nickname: Optional[str]


class BlogTag(SQLModel):
    tag_id: Optional[uuid.UUID]
    tag_name: Optional[str]


class BlogRead(SQLModel):
    id: uuid.UUID
    name: str
    date_created: datetime
    date_modified: datetime
    authors: List[BlogAuthor]
    tags: Optional[List[BlogTag]]
    likers: Optional[List[BlogLiker]]
    subscribers: Optional[List[BlogSubscriber]]


class BlogReadList(SQLModel):
    id: uuid.UUID
    name: str
    date_created: datetime
    date_modified: datetime


class ReadBlogsPagination(SQLModel):
    data: List[BlogReadList]
    pagination: Pagination
    sort: Sort

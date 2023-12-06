import uuid
from datetime import datetime
from enum import Enum
from typing import List, Optional

from sqlmodel import Field, SQLModel

from dw_blog.schemas.common import Pagination, Sort


class SortBlogBy(str, Enum):
    name = "name"
    date_created = "date_created"
    likers = "likers"
    subscribers = "subscribers"


class BlogBase(SQLModel):
    name: str = Field(
        min_length=3,
        max_length=500,
        nullable=False,
    )
    archived: bool = Field(default=False)
    date_created: datetime = Field(default_factory=datetime.utcnow)
    date_modified: datetime = Field(default_factory=datetime.utcnow)


class BlogCreate(SQLModel):
    name: str = Field(
        min_length=3,
        max_length=500,
        nullable=False,
    )
    categories_id: List[uuid.UUID]


class BlogUpdate(SQLModel):
    name: Optional[str] = Field(
        min_length=3,
        max_length=500,
        nullable=True,
    )
    archived: Optional[bool] = False
    add_categories_id: Optional[List[uuid.UUID]] = None
    remove_categories_id: Optional[List[uuid.UUID]] = None


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
    categories_name: List[str]
    date_created: datetime
    date_modified: datetime
    authors: List[BlogAuthor]
    tags: Optional[List[BlogTag]]
    likers: Optional[List[BlogLiker]]
    subscribers: Optional[List[BlogSubscriber]]
    archived: bool


class BlogReadList(SQLModel):
    id: uuid.UUID
    categories_name: List[str]
    name: str
    archived: bool
    subscription_count: int
    likes_count: int
    date_created: datetime
    date_modified: datetime


class ReadBlogsPagination(SQLModel):
    data: List[BlogReadList]
    pagination: Pagination
    sort: Sort

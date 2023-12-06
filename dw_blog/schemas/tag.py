import uuid
from datetime import datetime
from typing import List
from enum import Enum

from sqlmodel import Field, SQLModel

from dw_blog.schemas.common import Pagination, Sort


class SortTagBy(str, Enum):
    most_subscribers = "most_subscribers"
    date_created = "date_created"


class TagBase(SQLModel):
    name: str = Field(
        min_length=3,
        max_length=500,
        nullable=False,
    )
    date_created: datetime = Field(default_factory=datetime.utcnow)
    date_modified: datetime = Field(default_factory=datetime.utcnow)


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


class TagUpdate(SQLModel):
    name: str = Field(
        min_length=3,
        max_length=500,
        nullable=False,
        regex=r"#\w+",
    )

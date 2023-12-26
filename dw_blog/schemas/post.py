from enum import Enum
import uuid
from datetime import datetime
from typing import Optional, List

from sqlmodel import Field, SQLModel

from dw_blog.schemas.common import Pagination, Sort


class SortPostBy(str, Enum):
    title = "name"
    date_created = "date_created"
    likers = "likers"


class PostBase(SQLModel):
    title: str = Field(min_length=3, max_length=500, nullable=False)
    body: str = Field(min_length=50, max_length=10000, nullable=False)
    published: bool = Field(nullable=False, default_factory=False)
    date_created: datetime = Field(default_factory=datetime.utcnow)
    date_modified: datetime = Field(default_factory=datetime.utcnow)


class PostCreate(SQLModel):
    title: str = Field(min_length=3, max_length=500, nullable=False)
    body: str = Field(min_length=50, max_length=10000, nullable=False)
    published: bool = Field(nullable=False, default_factory=False)
    bibliography: Optional[List[str]] = None
    notes: Optional[List[str]] = None
    tags_ids: List[uuid.UUID]
    authors_ids: List[uuid.UUID]
    blog_id: uuid.UUID


class TagInPost(SQLModel):
    id: uuid.UUID
    name: str


class AuthorInPost(SQLModel):
    id: uuid.UUID
    nickname: str


class BlogInPost(SQLModel):
    id: uuid.UUID
    name: str


class LikerOfPost(SQLModel):
    id: uuid.UUID
    nickname: str


class PostRead(PostBase):
    id: uuid.UUID
    notes: Optional[List[str]] = None
    bibliography: Optional[List[str]] = None
    tags: List[TagInPost]
    authors: List[AuthorInPost]
    likers: Optional[List[LikerOfPost]] = None
    blog: BlogInPost


class PostsRead(PostRead):
    likes_count: int


class PostUpdate(SQLModel):
    title: Optional[str] = Field(min_length=3, max_length=500, nullable=True)
    body: Optional[str] = Field(min_length=50, max_length=10000, nullable=True)
    published: Optional[bool] = None
    bibliography: Optional[List[str]] = None
    notes: Optional[List[str]] = None
    tags_ids: Optional[List[uuid.UUID]] = None
    authors_ids: Optional[List[uuid.UUID]]


class PostDelete(SQLModel):
    id: uuid.UUID


class ReadBlogsPagination(SQLModel):
    data: List[PostsRead]
    pagination: Pagination
    sort: Sort

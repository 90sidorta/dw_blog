import uuid
from datetime import datetime
from typing import List

from sqlmodel import Field, Relationship, SQLModel

from dw_blog.models.tag import Tag, TagPosts


class PostBase(SQLModel):
    text: str = Field(
        min_length=3,
        max_length=30000,
        nullable=False,
    )
    date_created: datetime = Field(default_factory=datetime.utcnow)
    date_modified: datetime = Field(default_factory=datetime.utcnow)
    blog_id: uuid.UUID = Field(nullable=False)
    author_id: uuid.UUID = Field(nullable=False)
    author_nickname: str = Field(nullable=False)
    published: bool = Field(nullable=False, default_factory=False)


class Post(PostBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    comments: List["Comment"] = Relationship(back_populates="post")
    tags: List[Tag] = Relationship(
        back_populates="posts",
        link_model=TagPosts,
    )


class PostCreate(SQLModel):
    text: str = Field(
        min_length=3,
        max_length=30000,
        nullable=False,
    )


class PostRead(Post):
    pass


class PostUpdate(PostCreate):
    pass


class PostDelete(SQLModel):
    id: uuid.UUID

import uuid
from typing import List
from datetime import datetime

from sqlmodel import SQLModel, Field, Relationship


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
    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        index=True
    )
    posts: List["Post"] = Relationship(back_populates="tags", link_model=TagPosts)


class TagCreate(SQLModel):
    name: str = Field(
        min_length=3,
        max_length=500,
        nullable=False,
        regex=r'#\w+',
    )


class TagRead(TagBase):
    id: uuid.UUID


class TagUpdate(TagCreate):
    pass


class TagDelete(TagRead):
    pass

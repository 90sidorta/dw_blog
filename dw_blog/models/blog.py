import uuid
from typing import List
from datetime import datetime

from sqlmodel import SQLModel, Field, Relationship


class BlogAuthors(SQLModel, table=True):
    blog_id: uuid.UUID = Field(foreign_key="blog.id", primary_key=True)
    author_id: uuid.UUID = Field(foreign_key="user.id", primary_key=True)


class BlogBase(SQLModel):
    name: str = Field(
        min_length=3,
        max_length=500,
        nullable=False,
    )
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
    tags: List["Tag"] = Relationship(back_populates="blog")

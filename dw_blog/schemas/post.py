import uuid
from datetime import datetime

from sqlmodel import Field, SQLModel


class PostBase(SQLModel):
    title: str = Field(min_length=3, max_length=500, nullable=False)
    body: str = Field(min_length=50, max_length=10000, nullable=False)
    published: bool = Field(nullable=False, default_factory=False)
    date_created: datetime = Field(default_factory=datetime.utcnow)
    date_modified: datetime = Field(default_factory=datetime.utcnow)


class PostCreate(SQLModel):
    text: str = Field(
        min_length=3,
        max_length=30000,
        nullable=False,
    )


class PostRead(PostBase):
    id: uuid.UUID


class PostUpdate(PostCreate):
    pass


class PostDelete(SQLModel):
    id: uuid.UUID

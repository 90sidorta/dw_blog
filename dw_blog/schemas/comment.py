import uuid
from datetime import datetime

from sqlmodel import Field, SQLModel


class CommentBase(SQLModel):
    text: str = Field(
        min_length=3,
        max_length=10000,
        nullable=False,
    )
    date_created: datetime = Field(default_factory=datetime.utcnow)
    date_modified: datetime = Field(default_factory=datetime.utcnow)
    user_id: uuid.UUID = Field(nullable=False)
    user_nickname: str = Field(nullable=False)


class CommentCreate(SQLModel):
    text: str = Field(
        min_length=3,
        max_length=10000,
        nullable=False,
    )


class CommentRead(CommentBase):
    pass


class CommentUpdate(CommentCreate):
    pass


class CommentDelete(SQLModel):
    id: uuid.UUID

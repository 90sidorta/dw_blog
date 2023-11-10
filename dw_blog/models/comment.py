import uuid
from datetime import datetime

from sqlmodel import SQLModel, Field, Relationship

from dw_blog.models.post import Post


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


class Comment(CommentBase, table=True):
    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        index=True
    )
    post_id: uuid.UUID = Field(foreign_key="post.id")
    post: Post = Relationship(back_populates="comments")


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

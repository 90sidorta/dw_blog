import uuid

from sqlmodel import Field, Relationship

from dw_blog.models.post import Post
from dw_blog.schemas.comment import CommentBase


class Comment(CommentBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    post_id: uuid.UUID = Field(foreign_key="post.id")
    post: Post = Relationship(back_populates="comments")

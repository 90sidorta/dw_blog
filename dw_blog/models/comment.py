import uuid

from sqlmodel import Field, Relationship

# from dw_blog.models import User
from dw_blog.models.post import Post
from dw_blog.schemas.comment import CommentBase


class Comment(CommentBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    post_id: uuid.UUID = Field(foreign_key="post.id")
    post: Post = Relationship(back_populates="comments")
    # TODO: Add author_id and author fields
    # author_id: uuid.UUID = Field(foreign_key="user.id")
    # author: User = Relationship(back_populates="comments")

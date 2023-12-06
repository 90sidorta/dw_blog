import uuid
from typing import List

from sqlmodel import Field, Relationship

from dw_blog.schemas.post import PostBase
from dw_blog.models.tag import Tag, TagPosts


class Post(PostBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    comments: List["Comment"] = Relationship(back_populates="post")
    tags: List[Tag] = Relationship(
        back_populates="posts",
        link_model=TagPosts,
    )

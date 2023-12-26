import uuid
from typing import List, Optional

from sqlmodel import Field, Relationship

from dw_blog.models.blog import Blog, BlogAuthors, BlogLikes, BlogSubscribers
from dw_blog.models.tag import TagSubscribers, Tag
from dw_blog.models.post import Post, PostAuthors, PostLikers, PostFavourites
# from dw_blog.models.category import Category, CategoryFavourite
from dw_blog.schemas.user import UserBase


class User(UserBase, table=True):
    __tablename__ = "user"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    blogs: Optional[List[Blog]] = Relationship(
        back_populates="authors",
        link_model=BlogAuthors,
    )
    liked_blogs: Optional[List[Blog]] = Relationship(
        back_populates="likers",
        link_model=BlogLikes,
    )
    subscribed_blogs: Optional[List[Blog]] = Relationship(
        back_populates="subscribers",
        link_model=BlogSubscribers,
    )
    subscribed_tags: Optional[List[Tag]] = Relationship(
        back_populates="subscribers",
        link_model=TagSubscribers,
    )
    liked_posts: Optional[List[Post]] = Relationship(
        back_populates="likers",
        link_model=PostLikers,
    )
    favourite_posts: Optional[List[Post]] = Relationship(
        back_populates="favouriters",
        link_model=PostFavourites,
    )
    posts: Optional[List[Post]] = Relationship(
        back_populates="authors",
        link_model=PostAuthors,
    )
    # categories: Optional[List[Category]] = Relationship(
    #     back_populates="favouriters",
    #     link_model=CategoryFavourite,
    # )

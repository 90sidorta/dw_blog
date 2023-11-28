from uuid import UUID
from typing import Optional

from sqlmodel import select, func, delete

from dw_blog.models.user import User
from dw_blog.models.common import SortOrder
from dw_blog.models.tag import Tag
from dw_blog.models.auth import AuthUser
from dw_blog.models.blog import (
    Blog,
    BlogAuthors,
    BlogLikes,
    BlogSubscribers,
    SortBlogBy,
)

UserLiker = User.__table__.alias()
UserSubscriber = User.__table__.alias()


def get_single_blog_query(blog_id: UUID):
    q = (
        select(
            Blog.id,
            Blog.name,
            Blog.date_created,
            Blog.date_modified,
            func.array_agg(func.distinct(User.id)).label("author_id"),
            func.array_agg(func.distinct(User.nickname)).label("author_nickname"),
            func.array_agg(func.distinct(Tag.id)).label("tag_id"),
            func.array_agg(func.distinct(Tag.name)).label("tag_name"),
            func.array_agg(func.distinct(UserLiker.c.id)).label("likers_id"),
            func.array_agg(func.distinct(UserLiker.c.nickname)).label("likers_nicknames"),
            func.array_agg(func.distinct(UserSubscriber.c.id)).label("subscriber_id"),
            func.array_agg(func.distinct(UserSubscriber.c.nickname)).label("subscriber_nicknames"),
            Blog.archived,
        )
        .join(BlogAuthors, onclause=Blog.id == BlogAuthors.blog_id, isouter=True)
        .join(User, onclause=BlogAuthors.author_id == User.id, isouter=True)
        .join(BlogLikes, onclause=Blog.id == BlogLikes.blog_id, isouter=True)
        .join(UserLiker, onclause=BlogLikes.liker_id == UserLiker.c.id, isouter=True)
        .join(BlogSubscribers, onclause=Blog.id == BlogSubscribers.blog_id, isouter=True)
        .join(UserSubscriber, onclause=BlogSubscribers.subscriber_id == UserSubscriber.c.id, isouter=True)
        .join(Tag, onclause=Blog.id == Tag.blog_id, isouter=True)
        .where(Blog.id == blog_id)
        .group_by(Blog.id)
    )
    return q


def get_listed_blogs_query(
    limit: int,
    offset: int,
    blog_name: Optional[str] = None,
    author_id: Optional[UUID] = None,
    sort_order: SortOrder = SortOrder.ascending,
    sort_by: SortBlogBy = SortBlogBy.date_created,
):
    # Create query
    q = select(Blog)

    # Get records based on blog name
    if blog_name:
        q = q.where(Blog.name.ilike(f"%{blog_name}%"))

    # Get records based on blog author id
    if author_id:
        q = (
            q.join(BlogAuthors, onclause=BlogAuthors.blog_id == Blog.id, isouter=True)
            .join(User, onclause=User.id == BlogAuthors.author_id, isouter=True)
            .where(User.id == author_id)
        )

    # Create sorting
    if sort_by == SortBlogBy.date_created:
        if sort_order == SortOrder.ascending:
            q = q.order_by(Blog.date_created)
        else:
            q = q.order_by(Blog.date_created.desc())

    if sort_by == SortBlogBy.name:
        if sort_order == SortOrder.ascending:
            q = q.order_by(Blog.name)
        else:
            q = q.order_by(Blog.name.desc())

    # Assign query for count of all records
    q_all = q
    # Add pagination to query
    q_pag = q.limit(limit).offset(offset)
    return q_pag, q_all


def is_author_query(
    blog_id: UUID,
    author_id: UUID,
):
    q = select(BlogAuthors).where(
        BlogAuthors.blog_id == blog_id,
        BlogAuthors.author_id == author_id,
    )
    return q


def delete_author_query(
    remove_author_id: UUID,
    blog_id: UUID,
):
    q = delete(BlogAuthors).where(
        (BlogAuthors.author_id == remove_author_id),
        (BlogAuthors.blog_id == blog_id),
    )
    return q


def check_subscription_query(
    blog_id: UUID,
    current_user: AuthUser,
):
    q = select(BlogSubscribers).where(
        BlogSubscribers.blog_id == blog_id,
        BlogSubscribers.subscriber_id == current_user["user_id"],
    )
    return q


def check_like_query(
    blog_id: UUID,
    current_user: AuthUser,
):
    q = select(BlogLikes).where(
        BlogLikes.blog_id == blog_id,
        BlogLikes.liker_id == current_user["user_id"],
    )
    return q

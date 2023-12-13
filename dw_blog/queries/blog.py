from typing import Optional, Union, List
from uuid import UUID
from functools import reduce

from sqlmodel import delete, func, select, or_

from dw_blog.schemas.auth import AuthUser
from dw_blog.models.blog import Blog, BlogAuthors, BlogLikes, BlogSubscribers
from dw_blog.schemas.blog import SortBlogBy
from dw_blog.schemas.common import SortOrder
from dw_blog.models.tag import Tag
from dw_blog.models.user import User
from dw_blog.models.category import Category, CategoryBlogs

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
            func.array_agg(func.distinct(Category.name)).label("categories_name"),
        )
        .join(BlogAuthors, onclause=Blog.id == BlogAuthors.blog_id, isouter=True)
        .join(User, onclause=BlogAuthors.author_id == User.id, isouter=True)
        .join(BlogLikes, onclause=Blog.id == BlogLikes.blog_id, isouter=True)
        .join(UserLiker, onclause=BlogLikes.liker_id == UserLiker.c.id, isouter=True)
        .join(BlogSubscribers, onclause=Blog.id == BlogSubscribers.blog_id, isouter=True)
        .join(UserSubscriber, onclause=BlogSubscribers.subscriber_id == UserSubscriber.c.id, isouter=True)
        .join(Tag, onclause=Blog.id == Tag.blog_id, isouter=True)
        .join(CategoryBlogs, onclause=Blog.id == CategoryBlogs.blog_id, isouter=True)
        .join(Category, onclause=CategoryBlogs.category_id == Category.id, isouter=True)
        .where(Blog.id == blog_id)
        .group_by(Blog.id)
    )
    return q


def get_listed_blogs_query(
    limit: int,
    offset: int,
    blog_name: Optional[str] = None,
    author_id: Optional[UUID] = None,
    archived: Optional[Union[bool, None]] = None,
    categories_ids: Optional[List[UUID]] = None,
    sort_order: SortOrder = SortOrder.ascending,
    sort_by: SortBlogBy = SortBlogBy.date_created,
):
    # Create query
    sub_q = (
        select(
            Blog.id.label("id"),
            func.array_agg(func.distinct(Category.id)).label("categories_ids"),
            func.array_agg(func.distinct(Category.name)).label("categories_name"),
            Blog.archived.label("archived"),
            Blog.name.label("name"),
            Blog.date_created.label("date_created"),
            Blog.date_modified.label("date_modified"),
            func.count(func.distinct(BlogSubscribers.subscriber_id)).label("subscription_count"),
            func.count(func.distinct(BlogLikes.liker_id)).label("likes_count"),
        )
        .join(CategoryBlogs, onclause=Blog.id == CategoryBlogs.blog_id, isouter=True)
        .join(Category, onclause=CategoryBlogs.category_id == Category.id, isouter=True)
        .join(BlogSubscribers, onclause=BlogSubscribers.blog_id == Blog.id, isouter=True)
        .join(BlogLikes, onclause=BlogLikes.blog_id == Blog.id, isouter=True)
        .group_by(Blog.id)
        .alias()
    )
    q = select(
        sub_q.c.id,
        sub_q.c.categories_ids,
        sub_q.c.categories_name,
        sub_q.c.archived,
        sub_q.c.name,
        sub_q.c.date_created,
        sub_q.c.date_modified,
        sub_q.c.subscription_count,
        sub_q.c.likes_count,
    )

    # Get archived/active blogs only
    if archived is not None:
        if archived == True:
            q = q.where(sub_q.c.archived == True)
        else: 
            q = q.where(sub_q.c.archived == False)

    # Get records based on blog name
    if blog_name:
        q = q.where(sub_q.c.name.ilike(f"%{blog_name}%"))

    # Get records based on blog author id
    if author_id:
        q = (
            q.join(BlogAuthors, onclause=BlogAuthors.blog_id == sub_q.c.id, isouter=True)
            .join(User, onclause=User.id == BlogAuthors.author_id, isouter=True)
            .where(User.id == author_id)
        )

    # Get records based on category id
    if categories_ids:
        conditions = [sub_q.c.categories_ids.any(category_id) for category_id in categories_ids]
        q = q.where(or_(*conditions))

    # Create sorting
    if sort_by == SortBlogBy.date_created:
        if sort_order == SortOrder.ascending:
            q = q.order_by(sub_q.c.date_created)
        else:
            q = q.order_by(sub_q.c.date_created.desc())

    if sort_by == SortBlogBy.subscribers:
        if sort_order == SortOrder.ascending:
            q = q.order_by(sub_q.c.subscription_count)
        else:
            q = q.order_by(sub_q.c.subscription_count.desc())

    if sort_by == SortBlogBy.likers:
        if sort_order == SortOrder.ascending:
            q = q.order_by(sub_q.c.likes_count)
        else:
            q = q.order_by(sub_q.c.likes_count.desc())

    if sort_by == SortBlogBy.name:
        if sort_order == SortOrder.ascending:
            q = q.order_by(sub_q.c.name)
        else:
            q = q.order_by(sub_q.c.name.desc())

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

from uuid import UUID
from typing import Optional

from sqlmodel import select, func

from dw_blog.models.tag import Tag, SortTagBy, TagSubscribers
from dw_blog.models.blog import Blog
from dw_blog.models.common import SortOrder
from dw_blog.exceptions.tag import TagListingBothFilters
from dw_blog.models.auth import AuthUser


def get_single_tag_query(tag_id: UUID):
    q = (
        select(
            Tag.id,
            Tag.name,
            Tag.date_created,
            Tag.date_modified,
            Blog.id.label("blog_id"),
            Blog.name.label("blog_name"),
        )
        .join(
            Blog,
            onclause=Blog.id == Tag.blog_id,
            isouter=True,
        )
        .where(Tag.id == tag_id)
    )
    return q


def get_listed_tags_query(
    limit: int,
    offset: int,
    user_id: Optional[UUID] = None,
    blog_id: Optional[UUID] = None,
    tag_name: Optional[str] = None,
    sort_order: SortOrder = SortOrder.ascending,
    sort_by: SortTagBy = SortTagBy.most_subscribers,
):
    sub_q = (
        select(
            Tag.id.label("id"),
            Tag.name.label("name"),
            Tag.date_created.label("date_created"),
            Tag.date_modified.label("date_modified"),
            Tag.blog_id.label("blog_id"),
            func.count(func.distinct(TagSubscribers.subscriber_id)).label("subscription_count"),
            func.array_agg(func.distinct(TagSubscribers.subscriber_id)).label("subscribers_ids"),
        )
        .join(TagSubscribers, onclause=TagSubscribers.tag_id == Tag.id, isouter=True)
        .group_by(Tag.id)
        .alias()
    )
    q = select(
        sub_q.c.id,
        sub_q.c.name,
        sub_q.c.date_created,
        sub_q.c.date_modified,
        sub_q.c.blog_id,
        sub_q.c.subscription_count,
        sub_q.c.subscribers_ids,
    )

    # Raise exception if both filters are defined
    if blog_id and user_id:
        raise TagListingBothFilters()

    # Filter by blog
    if blog_id:
        q = q.where(sub_q.c.blog_id == blog_id)

    # Filter by subscribed user
    if user_id:
        q = q.where(sub_q.c.subscribers_ids.any(user_id))

    # Filter by tag name
    if tag_name:
        q = q.where(sub_q.c.name.ilike(f"%{tag_name}%"))

    # Create sorting
    if sort_by == SortTagBy.most_subscribers:
        if sort_order == SortOrder.ascending:
            q = q.order_by(sub_q.c.subscription_count)
        else:
            q = q.order_by(sub_q.c.subscription_count.desc())

    if sort_by == SortTagBy.date_created:
        if sort_order == SortOrder.ascending:
            q = q.order_by(sub_q.c.date_created)
        else:
            q = q.order_by(sub_q.c.date_created.desc())

    # Assign query for count of all records
    q_all = q
    # Add pagination to query
    q_pag = q.limit(limit).offset(offset)
    return q_pag, q_all


def tag_subscription_query(
    tag_id: UUID,
    current_user: AuthUser,
):
    q = select(TagSubscribers).where(
        TagSubscribers.tag_id == tag_id,
        TagSubscribers.subscriber_id == current_user["user_id"],
    )
    return q

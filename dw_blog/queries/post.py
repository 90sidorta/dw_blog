
from typing import List, Optional
from uuid import UUID

from sqlmodel import select, func, or_
from dw_blog.models.blog import Blog

from dw_blog.models.post import Post, PostAuthors, PostLikers
from dw_blog.models.tag import Tag, TagPosts
from dw_blog.models.user import User
from dw_blog.schemas.common import SortOrder
from dw_blog.schemas.post import SortPostBy

UserLiker = User.__table__.alias()


def get_listed_posts_query(
    limit: int,
    offset: int,
    published: bool,
    blog_id: Optional[UUID] = None,
    authors_ids: Optional[List[UUID]] = None,
    tags_ids: Optional[List[UUID]] = None,
    title_search: Optional[str] = None,
    body_search: Optional[str] = None,
    sort_order: SortOrder = SortOrder.ascending,
    sort_by: SortPostBy = SortPostBy.date_created,
):
    sub_q = (
        select(
            Post.id.label("id"),
            Post.date_created.label("date_created"),
            Post.date_modified.label("date_modified"),
            Post.notes.label("notes"),
            Post.bibliography.label("bibliography"),
            Post.published.label("published"),
            Post.title.label("title"),
            Post.body.label("body"),
            Blog.id.label("blog_id"),
            Blog.name.label("blog_name"),
            func.array_agg(func.distinct(Tag.id)).label("tags_ids"),
            func.array_agg(func.distinct(Tag.name)).label("tags_names"),
            func.array_agg(func.distinct(User.id)).label("authors_ids"),
            func.array_agg(func.distinct(User.nickname)).label("authors_nicknames"),
            func.array_agg(func.distinct(UserLiker.c.id)).label("likers_ids"),
            func.array_agg(func.distinct(UserLiker.c.nickname)).label("likers_nicknames"),
            func.count(func.distinct(UserLiker.c.id)).label("likes_count"),
        )
        .join(Blog, onclause=Blog.id == Post.blog_id, isouter=True)
        .join(TagPosts, onclause=TagPosts.post_id == Post.id, isouter=True)
        .join(Tag, onclause=Tag.id == TagPosts.tag_id, isouter=True)
        .join(PostAuthors, onclause=PostAuthors.post_id == Post.id, isouter=True)
        .join(User, onclause=User.id == PostAuthors.author_id, isouter=True)
        .join(PostLikers, onclause=PostLikers.post_id == Post.id, isouter=True)
        .join(UserLiker, onclause=UserLiker.c.id == PostLikers.liker_id, isouter=True)
        .group_by(Post.id, Blog.id)
        .alias()
    )
    q = select(
        sub_q.c.id,
        sub_q.c.blog_id,
        sub_q.c.blog_name,
        sub_q.c.date_created,
        sub_q.c.date_modified,
        sub_q.c.notes,
        sub_q.c.bibliography,
        sub_q.c.published,
        sub_q.c.title,
        sub_q.c.body,
        sub_q.c.tags_ids,
        sub_q.c.tags_names,
        sub_q.c.authors_ids,
        sub_q.c.authors_nicknames,
        sub_q.c.likers_ids,
        sub_q.c.likers_nicknames,
        sub_q.c.likes_count,
    )

    # Filter by blog_id
    if blog_id:
        q = q.where(sub_q.c.blog_id == blog_id)

    # Filter by published
    if published:
        q = q.where(sub_q.c.published == published)

    # Filter by authors_ids
    if authors_ids:
        conditions = [sub_q.c.authors_ids.any(author_id) for author_id in authors_ids]
        q = q.where(or_(*conditions))
    
    # Filter by tags_ids
    if tags_ids:
        conditions = [sub_q.c.tags_ids.any(tag_id) for tag_id in tags_ids]
        q = q.where(or_(*conditions))

    # Filter by title_search
    if title_search:
        q = q.where(sub_q.c.title.ilike(f"%{title_search}%"))

    # Filter by body_search
    if body_search:
        q = q.where(sub_q.c.body.ilike(f"%{body_search}%"))

    # Create sorting
    if sort_by == SortPostBy.date_created:
        if sort_order == SortOrder.ascending:
            q = q.order_by(sub_q.c.date_created.asc())
        else:
            q = q.order_by(sub_q.c.date_created.desc())
    elif sort_by == SortPostBy.title:
        if sort_order == SortOrder.ascending:
            q = q.order_by(sub_q.c.title.asc())
        else:
            q = q.order_by(sub_q.c.title.desc())
    elif sort_by == SortPostBy.likers:
        if sort_order == SortOrder.ascending:
            q = q.order_by(sub_q.c.likes_count)
        else:
            q = q.order_by(sub_q.c.likes_count.desc())

    # Assign query for count of all records
    q_all = q
    # Add pagination to query
    q_pag = q.limit(limit).offset(offset)

    return q_pag, q_all

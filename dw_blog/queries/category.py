from uuid import UUID
from typing import Optional

from sqlmodel import func, select, literal_column, text

from dw_blog.models.category import Category, CategoryBlogs
from dw_blog.schemas.category import SortCategoryBy
from dw_blog.schemas.common import SortOrder
from dw_blog.models.blog import Blog, BlogLikes


CategoryBlogsBlogId = CategoryBlogs.__table__.alias()

def get_single_category_query(category_id: UUID):
    q = (
            select(
                Category.id.label("id"),
                Category.name.label("name"),
                Category.approved.label("approved"),
                Category.date_created.label("date_created"),
                Category.date_modified.label("date_modified"),
                func.array_agg(Blog.id).label("blog_ids"),
                func.array_agg(Blog.name).label("blog_names"),
            )
            .join(CategoryBlogs, onclause=CategoryBlogs.category_id == Category.id, isouter=True)
            .join(Blog, onclause=Blog.id == CategoryBlogs.blog_id, isouter=True)
            .where(Category.id == category_id)
            .group_by(Category.id)
    )
    return q


def get_listed_categories_query(
    limit: int,
    offset: int,
    category_name: Optional[str] = None,
    approved: Optional[bool] = None,
    sort_order: SortOrder = SortOrder.ascending,
    sort_by: SortCategoryBy = SortCategoryBy.date_created,
):
    # Create subquery
    subquery = (
        select(
            Blog.id,
            Blog.name,
            func.count(func.distinct(BlogLikes.liker_id)).label('likes_count')
        )
        .select_from(Blog)
        .join(BlogLikes, BlogLikes.blog_id == Blog.id, isouter=True)
        .join(CategoryBlogs, CategoryBlogs.blog_id == Blog.id, isouter=True)
        .where(CategoryBlogs.category_id == Category.id)
        .group_by(Blog.id, CategoryBlogs.category_id)
        .order_by(func.count(func.distinct(BlogLikes.liker_id)).desc())
        .limit(5)
        .lateral()
    ).alias('subquery')

    # Create query
    q = (
        select(
            Category.id,
            Category.name,
            Category.approved,
            Category.date_created,
            Category.date_modified,
            func.array_agg(func.distinct(subquery.c.id)).label('blog_ids'),
            func.array_agg(func.distinct(subquery.c.name)).label('blog_names'),
            func.count(func.distinct(CategoryBlogsBlogId.c.blog_id)).label('blogs_count')
        )
        .select_from(Category)
        .join(CategoryBlogsBlogId, CategoryBlogsBlogId.c.category_id == Category.id, isouter=True)
        .join(subquery, text('true'), isouter=True)
        .group_by(Category.id)
    )

    if category_name:
        q = q.where(Category.name.ilike(f"%{category_name}%"))

    if approved is not None:
        q = q.where(Category.approved == approved)

    # Create sorting by most liked blog
    if sort_by == SortCategoryBy.blogs_with_most_likes:
        sort_most_likes = func.coalesce(func.array_agg(subquery.c.likes_count)[1], literal_column('0'))
        if sort_order == SortOrder.ascending:
            q = q.order_by(sort_most_likes)
        if sort_order == SortOrder.descending:
            q = q.order_by(sort_most_likes.desc())

    # Create sorting by most blogs
    if sort_by == SortCategoryBy.most_blogs:
        sort_most_blogs = func.count(func.distinct(CategoryBlogsBlogId.c.blog_id))
        if sort_order == SortOrder.ascending:
            q = q.order_by(sort_most_blogs)
        if sort_order == SortOrder.descending:
            q = q.order_by(sort_most_blogs.desc())

    # Create sorting by date created
    if sort_by == SortCategoryBy.date_created:
        if sort_order == SortOrder.ascending:
            q = q.order_by(Category.date_created)
        else:
            q = q.order_by(Category.date_created.desc())

    # Create sorting by name
    if sort_by == SortCategoryBy.name:
        if sort_order == SortOrder.ascending:
            q = q.order_by(Category.name)
        else:
            q = q.order_by(Category.name.desc())

    q_all = q
    q_pag = q.limit(limit).offset(offset)

    return q_pag, q_all


def get_blogs_for_category_query(category_id: UUID):
    q = (
            select(
                CategoryBlogs.blog_id
            )
            .where(CategoryBlogs.category_id == category_id)
            .group_by(CategoryBlogs.blog_id)
    )
    return q

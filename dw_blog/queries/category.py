from uuid import UUID

from sqlmodel import func, select

from dw_blog.models.category import Category, CategoryBlogs
from dw_blog.models.blog import Blog

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
from typing import Optional, List
from datetime import datetime
from uuid import UUID

from fastapi import Depends, HTTPException, status
from sqlmodel import Session, select
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import selectinload

from dw_blog.db.db import get_session
from dw_blog.models.blog import BlogBase, BlogRead, Blog, BlogAuthors, BlogAuthor
from dw_blog.db.db import get_session
from dw_blog.utils.auth import check_if_admin
from dw_blog.models.auth import AuthUser
from dw_blog.models.user import User
from dw_blog.services.user import UserService


class BlogService:
    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.user_service = UserService(db_session)

    async def create(
        self,
        current_user: AuthUser,
        name: str,
    ) -> BlogRead:
        user = await self.user_service.get(
            user_id=str(current_user["user_id"])
        )

        # Check if user has less than 3 blogs
        q = select(BlogAuthors).where(BlogAuthors.author_id == user.id)
        result = await self.db_session.exec(q)
        user_blogs = result.fetchall()
        if len(user_blogs) >= 3:
            raise HTTPException(
                detail="User already has 3 blogs!",
                status_code=status.HTTP_403_FORBIDDEN,
            )

        try:
            blog = Blog(
                name=name,
                date_created=datetime.now(),
                date_modified=datetime.now(),
                authors=[user]
            )
            self.db_session.add(blog)
            await self.db_session.commit()
            await self.db_session.refresh(blog)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to add blog!",
            )

        blog_read = await self.get(blog_id=blog.id)

        return blog_read

    async def get(
        self,
        blog_id: UUID,
    ) -> BlogRead:
        q = (
            select(
                Blog.id,
                Blog.name,
                Blog.date_created,
                Blog.date_modified,
                User.id.label("author_id"),
                User.nickname.label("author_nickname"),
            )
            .join(BlogAuthors, onclause=Blog.id == BlogAuthors.blog_id, isouter=True)
            .join(User, onclause=BlogAuthors.author_id == User.id, isouter=True)
            .where(Blog.id == blog_id)
        )
        result = await self.db_session.exec(q)
        blogs = result.all()

        if len(blogs) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Blog not found!"
            )
        
        authors = []
        for blog in blogs:
            authors.append(
                BlogAuthor(
                    author_id=blog.author_id,
                    nickname=blog.author_nickname,
                )
            )

        blog_read = BlogRead(
            id=blog.id,
            name=blog.name,
            date_created=blog.date_created,
            date_modified=blog.date_modified,
            authors=authors
        )
        
        return blog_read

    async def list(
        self,
        author_name: Optional[str] = None,
        blog_name: Optional[str] = None,
    ):
        if blog_name:
            q = select(Blog).where(Blog.name.ilike(f"%{blog_name}%"))
            result = await self.db_session.exec(q)
            blogs = result.fetchall()
        
        if author_name:
            users = await self.user_service.list(nickname=author_name)
            blogs = []
            for user in users:
                user_blogs_results = await self.db_session.exec(
                    select(Blog)
                    .join(BlogAuthors, onclause=Blog.id == BlogAuthors.blog_id, isouter=True)
                    .where(BlogAuthors.author_id == user.id)
                )
                user_blogs = user_blogs_results.fetchall()
                for user_blog in user_blogs:
                    blogs.append(user_blog)

        if len(blogs) == 0:
            raise HTTPException(
                detail="No blogs found!",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        return_blogs = []
        for blog in blogs:
            print("blog", blog)
            return_blogs.append(await self.get(blog_id=blog.id))
        
        return return_blogs

async def get_blog_service(session: AsyncSession = Depends(get_session)):
    yield BlogService(session)

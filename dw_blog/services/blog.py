from typing import Optional, List
from datetime import datetime
from uuid import UUID

from fastapi import Depends, HTTPException, status
from sqlmodel import Session, select
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import selectinload

from dw_blog.db.db import get_session
from dw_blog.models.blog import BlogBase, BlogRead, Blog, BlogAuthors
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

        return blog

    async def get(
        self,
        blog_id: UUID,
    ):
        # Tutaj trzeba zrobić tak żeby zwracało jeden blog, ale dwóch autorów
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
        blog = result.first()

        if blog is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Blog not found!"
            )
        
        print(213, blog)
        
        return blog

async def get_blog_service(session: AsyncSession = Depends(get_session)):
    yield BlogService(session)

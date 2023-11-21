from typing import Optional, List
from datetime import datetime
from uuid import UUID

from fastapi import Depends, HTTPException, status
from sqlmodel import Session, select
from sqlmodel.ext.asyncio.session import AsyncSession

from dw_blog.db.db import get_session
from dw_blog.models.tag import TagRead, Tag
from dw_blog.exceptions.tag import TagFailedAdd
from dw_blog.db.db import get_session
from dw_blog.utils.auth import check_if_admin
from dw_blog.models.auth import AuthUser
from dw_blog.services.user import UserService
from dw_blog.services.blog import BlogService


class TagService:
    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.user_service = UserService(db_session)
        self.blog_service = BlogService(db_session)

    async def create(
        self,
        current_user: AuthUser,
        blog_id: UUID,
        name: str,
    ) -> TagRead:
        """Add new tag for the specifed blog
        Args:
            current_user (AuthUser): current author object
            blog_id (UUID): id of the blog
            name (str): name of the tag
        Raises:
            TagFailedAdd: raised if tag addition failed
        Returns:
            TagRead: readable tag data
        """
        # Check if user is author of the blog
        await self.blog_service.check_blog(
            blog_id=blog_id,
            current_user=current_user,
        )

        # Create new tag object
        tag = Tag(
            text=name,
            blog_id=blog_id,
            date_created=datetime.now(),
            date_modified=datetime.now(),
        )
        # Add new tag to database
        try:
            self.db_session.add(tag)
            await self.db_session.commit()
            await self.db_session.refresh(tag)
        except Exception:
            raise TagFailedAdd(
                blog_id=blog_id,
                tag_name=name,
            )

        return await self.get(tag_id=tag.id)

    async def get(
        self,
        tag_id: UUID,
    ) -> TagRead:
        q = select(Tag).where(Tag.id == tag_id)
        result = await self.db_session.exec(q)
        tag = result.first()

        if tag is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tag not found!"
            )
        
        return tag

async def get_tag_service(session: AsyncSession = Depends(get_session)):
    yield TagService(session)
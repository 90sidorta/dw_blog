from datetime import datetime
from uuid import UUID

from fastapi import Depends
from sqlmodel import Session, select
from sqlmodel.ext.asyncio.session import AsyncSession

from dw_blog.db.db import get_session
from dw_blog.models.tag import TagRead, Tag
from dw_blog.exceptions.tag import (
    TagFailedAdd,
    TagNotFound,
    TagUpdateFail,
    TagDeleteFail,
)
from dw_blog.db.db import get_session
from dw_blog.models.auth import AuthUser
from dw_blog.models.blog import Blog
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
            name=name,
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
        """Get single tag based on it's id
        Args:
            tag_id (UUID): tag of id
        Raises:
            TagNotFound: raised if no tag with
            matching id exists
        Returns:
            TagRead: Tag data with blog name and id
        """
        # Query to return tag with blog data
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
            .where(Tag.id == tag_id))
        result = await self.db_session.exec(q)
        tag = result.first()

        # Raise exception if no tag found
        if tag is None:
            raise TagNotFound(tag_id=tag_id)
        
        return tag

    async def update(
        self,
        tag_id: UUID,
        current_user: AuthUser,
        name: str,
    ) -> TagRead:
        """Updates tag data
        Args:
            tag_id (UUID): id of blog to be updated
            current_user (AuthUser): current user object
            name (str): new tag name
        Raises:
            TagUpdateFail: raised if tag update failed
        Returns:
            TagRead: Read tag
        """
        update_tag = await self.db_session.get(Tag, tag_id)
        await self.check_blog(
            blog_id=update_tag.blog_id,
            current_user=current_user,
        )

        # Update blog name
        if name:
            update_tag.name = name
        try:
            self.db_session.add(update_tag)
            await self.db_session.commit()
        except Exception:
            raise TagUpdateFail()

        return await self.get(tag_id=tag_id)

    async def delete(
        self,
        tag_id: UUID,
        current_user: AuthUser,
    ) -> None:
        """Deletes tag based on its id and
        user permissions
        Args:
            tag_id (UUID): tag id
            current_user (AuthUser): current user object
        Raises:
            TagDeleteFail: raised if failed to delete tag
        """
        delete_tag = await self.db_session.get(Tag, tag_id)
        await self.check_blog(
            blog_id=delete_tag.blog_id,
            current_user=current_user,
        )

        # Delete blog
        try:
            self.db_session.delete(delete_tag)
            self.db_session.commit()
        except Exception:
            raise TagDeleteFail()

async def get_tag_service(session: AsyncSession = Depends(get_session)):
    yield TagService(session)

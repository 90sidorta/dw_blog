from datetime import datetime
from uuid import UUID
from typing import Optional, Union, List

from fastapi import Depends
from sqlmodel import Session
from sqlmodel.ext.asyncio.session import AsyncSession

from dw_blog.db.db import get_session
from dw_blog.exceptions.tag import TagNotFound
from dw_blog.exceptions.common import EntityUpdateFail, EntityDeleteFail, EntityFailedAdd, PaginationLimitSurpassed
from dw_blog.models.auth import AuthUser
from dw_blog.models.tag import Tag, TagRead, TagReadList, SortTagBy
from dw_blog.services.blog import BlogService
from dw_blog.services.user import UserService
from dw_blog.queries.tag import get_single_tag_query, get_listed_tags_query
from dw_blog.models.common import SortOrder


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
            EntityFailedAdd: raised if tag addition failed
        Returns:
            TagRead: readable tag data
        """
        # Check if user is author of the blog
        await self.blog_service.check_blog_permissions(
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
            raise EntityFailedAdd(entity_name="tag")

        return await self.get(tag_id=tag.id)

    async def list(
        self,
        limit: int,
        offset: int,
        user_id: Optional[UUID] = None,
        blog_id: Optional[UUID] = None,
        sort_order: SortOrder = SortOrder.ascending,
        sort_by: SortTagBy = SortTagBy.most_subscribers,
    ) -> Union[List[TagReadList], int]:
        """Get tags based on it's id
        Args:
            limit [int]: up to how many results per page
            offset [int]: how many records should be skipped
            user_id (Optional[UUID], optional): Id of the user to get its subscribed tags. Defaults to None.
            blog_id (Optional[UUID], optional): Id of the blog to get its tags. Defaults to None.
            sort_order [SortOrder]: order of sorting retrieved records. Defaults to ascending.
            sort_by [SortTagBy]: prop to sort records by. Defaults to most_subscribers.
        Raises:
            PaginationLimitSurpassed: raised if limit was suprassed
        Returns:
            Union[List[TagReadList], int]: List of tags data and total count of tags
        """
        # Check limit
        if limit > 20:
            raise PaginationLimitSurpassed()
        # Create query
        q_pag, q_all = get_listed_tags_query(
            limit=limit,
            offset=offset,
            user_id=user_id,
            blog_id=blog_id,
            sort_order=sort_order,
            sort_by=sort_by,
        )

        # Execute queries with and without limit
        tags_result = await self.db_session.exec(q_pag)
        all_result = await self.db_session.exec(q_all)
        tags = tags_result.fetchall()
        total = all_result.fetchall()

        return tags, len(total)


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
        q = get_single_tag_query(tag_id=tag_id)
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
            EntityUpdateFail: raised if tag update failed
        Returns:
            TagRead: Read tag
        """
        update_tag = await self.db_session.get(Tag, tag_id)
        await self.blog_service.check_blog_permissions(
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
            raise EntityUpdateFail(entity_id=tag_id, entity_name="tag")

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
            EntityDeleteFail: raised if failed to delete tag
        """
        delete_tag = await self.db_session.get(Tag, tag_id)
        await self.blog_service.check_blog_permissions(
            blog_id=delete_tag.blog_id,
            current_user=current_user,
        )

        # Delete blog
        try:
            self.db_session.delete(delete_tag)
            self.db_session.commit()
        except Exception:
            raise EntityDeleteFail(entity_id=tag_id, entity_name="tag")


async def get_tag_service(session: AsyncSession = Depends(get_session)):
    yield TagService(session)

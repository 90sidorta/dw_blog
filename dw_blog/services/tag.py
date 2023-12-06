from datetime import datetime
from uuid import UUID
from typing import Optional, Union, List

from fastapi import Depends
from sqlmodel import Session, select
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import selectinload

from dw_blog.db.db import get_session
from dw_blog.exceptions.tag import TagNotFound, TagAlreadySubscribed, TagNotYetSubscribed
from dw_blog.exceptions.user import UserNotFound
from dw_blog.exceptions.common import EntityUpdateFail, EntityDeleteFail, EntityFailedAdd, PaginationLimitSurpassed
from dw_blog.models.auth import AuthUser
from dw_blog.models.tag import Tag, TagRead, TagReadList, SortTagBy
from dw_blog.models.user import User
from dw_blog.services.blog import BlogService
from dw_blog.queries.tag import get_single_tag_query, get_listed_tags_query, tag_subscription_query
from dw_blog.models.common import SortOrder


class TagService:
    def __init__(self, db_session: Session):
        self.db_session = db_session
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
            operation="add tag"
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
        tag_name: Optional[str] = None,
        sort_order: SortOrder = SortOrder.ascending,
        sort_by: SortTagBy = SortTagBy.most_subscribers,
    ) -> Union[List[TagReadList], int]:
        """Get tags based on it's id
        Args:
            limit [int]: up to how many results per page
            offset [int]: how many records should be skipped
            user_id (Optional[UUID], optional): Id of the user to get its subscribed tags. Defaults to None.
            blog_id (Optional[UUID], optional): Id of the blog to get its tags. Defaults to None.
            tag_name (Optional[str], optional): Name of the tag. Defaults to None.
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
            tag_name=tag_name,
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

    async def subscribe(
        self,
        tag_id: UUID,
        current_user: AuthUser,
    ) -> TagRead:
        """This function creates a new subscribe record
        Args:
            tag_id (UUID): id of the tag to be
            subscribed to
            current_user (AuthUser): current user object
        Raises:
            TagNotFound: raised if tag does not exist
            UserNotFound: raised if user not found
            TagAlreadySubscribed: raised if tag is already
            subscribed by the user
            EntityUpdateFail: raised if tag subscription
            failed
        Returns:
            TagRead: tag data
        """
        # Try to get the tag
        q = (select(Tag).options(selectinload(Tag.subscribers)).where(Tag.id == tag_id))
        sub_tag_results = await self.db_session.exec(q)
        if not (sub_tag := sub_tag_results.first()):
            raise TagNotFound(tag_id=tag_id)

        # Check if user is already a subscriber
        already_sub = [] if len(sub_tag.subscribers) == 0 else [str(subsciber.id) for subsciber in sub_tag.subscribers]
        if current_user["user_id"] in already_sub:
            raise TagAlreadySubscribed(tag_name=sub_tag.name)
        # Check if user exists
        if not (adding_user := await self.db_session.get(User, current_user["user_id"])):
            user_id = current_user["user_id"]
            raise UserNotFound(error_message=f"User with id {user_id} not found!")

        # Try to add new subscription
        try:
            sub_tag.subscribers.append(adding_user)
            self.db_session.add(sub_tag)
            await self.db_session.commit()
        except Exception:
            raise EntityUpdateFail(entity_id=tag_id, entity_name="tag")

        return await self.get(tag_id=tag_id)

    async def unsubscribe(
        self,
        tag_id: UUID,
        current_user: AuthUser,
    ) -> TagRead:
        """This function deletes tag subscription entry
        Args:
            tag_id (UUID): id of the tag to unsubscribe
            current_user (AuthUser): current user object
        Raises:
            TagNotFound: raised if tag does not exist
            UserNotFound: raised if user not found
            TagNotYetSubscribed: raised if tag was not
            subscribed by the user
            EntityUpdateFail: raised if tag subscription
            failed
        Returns:
            TagRead: tag data
        """
        # Check if tag exists
        tag = await self.get(tag_id=tag_id)
        
        # Check if user is a subscriber
        q = tag_subscription_query(tag_id=tag_id, current_user=current_user)
        sub_tag_result = await self.db_session.exec(q)
        if not (sub_tag := sub_tag_result.first()):
            raise TagNotYetSubscribed(tag_name=tag.name)

        # Delete subscription
        try:
            await self.db_session.delete(sub_tag)
            await self.db_session.commit()
        except Exception:
            raise EntityUpdateFail(entity_id=tag_id, entity_name="tag")
        return await self.get(tag_id=tag_id)

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
        if not (update_tag := await self.db_session.get(Tag, tag_id)):
            raise TagNotFound(tag_id=tag_id)
        await self.blog_service.check_blog_permissions(
            blog_id=update_tag.blog_id,
            current_user=current_user,
            operation="tag update",
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
        if not (delete_tag := await self.db_session.get(Tag, tag_id)):
            raise TagNotFound(tag_id=tag_id)
        await self.blog_service.check_blog_permissions(
            blog_id=delete_tag.blog_id,
            current_user=current_user,
            operation="tag delete",
        )

        # Delete blog
        try:
            self.db_session.delete(delete_tag)
            self.db_session.commit()
        except Exception:
            raise EntityDeleteFail(entity_id=tag_id, entity_name="tag")

async def get_tag_service(session: AsyncSession = Depends(get_session)):
    yield TagService(session)

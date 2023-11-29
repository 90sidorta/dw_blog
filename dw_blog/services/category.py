from datetime import datetime
from uuid import UUID

from fastapi import Depends
from sqlmodel import Session, select
from sqlmodel.ext.asyncio.session import AsyncSession

from dw_blog.db.db import get_session
from dw_blog.exceptions.category import CategoryFailedAdd, CategoryNotFound
from dw_blog.models.auth import AuthUser
from dw_blog.models.category import Category, CategoryRead
from dw_blog.models.user import User, UserType


class CategoryService:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    async def create(
        self,
        current_user: AuthUser,
        name: str,
    ) -> CategoryRead:
        """Add new category
        Args:
            current_user (AuthUser): current author object
            name (str): name of the category
        Raises:
            CategoryFailedAdd: raised if tag addition failed
        Returns:
            CategoryRead: readable category data
        """
        # Check if user is an admin
        user: User = await self.db_session.get(User, current_user["user_id"])

        # Create new tag object
        category = Category(
            name=name,
            approved=True if user.user_type == UserType.admin else False,
            date_created=datetime.now(),
            date_modified=datetime.now(),
        )
        # Add new tag to database
        try:
            self.db_session.add(category)
            await self.db_session.commit()
            await self.db_session.refresh(category)
        except Exception:
            raise CategoryFailedAdd(category_name=name)

        return await self.get(category_id=category.id)

    async def get(
        self,
        category_id: UUID,
    ) -> CategoryRead:
        """Get single category based on it's id
        Args:
            category_id (UUID): id of the category
        Raises:
            CategoryNotFound: raised if no tag with
            matching id exists
        Returns:
            CategoryRead: Tag data with blog name and id
        """
        # Query to return tag with blog data
        q = select(Category).where(Category.id == category_id)
        result = await self.db_session.exec(q)
        category = result.first()

        # Raise exception if no category found
        if category is None:
            raise CategoryNotFound(category_id=category_id)

        return category

async def get_category_service(session: AsyncSession = Depends(get_session)):
    yield CategoryService(session)

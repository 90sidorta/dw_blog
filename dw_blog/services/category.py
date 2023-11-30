from datetime import datetime
from uuid import UUID
from typing import Optional, Union, List

from fastapi import Depends
from sqlmodel import Session
from sqlmodel.ext.asyncio.session import AsyncSession

from dw_blog.db.db import get_session
from dw_blog.models.common import SortOrder
from dw_blog.exceptions.category import CategoryFailedAdd, CategoryNotFound
from dw_blog.exceptions.common import PaginationLimitSurpassed
from dw_blog.models.auth import AuthUser
from dw_blog.models.category import Category, CategoryRead, CategoryBlogRead, SortCategoryBy, CategoryReadList
from dw_blog.models.user import User, UserType
from dw_blog.queries.category import get_single_category_query, get_listed_categories_query



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
    ):
        # -> CategoryRead:
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
        q = get_single_category_query(category_id=category_id)
        result = await self.db_session.exec(q)
        category = result.first()

        # Raise exception if no category found
        if category is None:
            raise CategoryNotFound(category_id=category_id)

        return CategoryRead(
            id=category.id,
            name=category.name,
            approved=category.approved,
            date_created=category.date_created,
            date_modified=category.date_modified,
            blogs=[
                CategoryBlogRead(blog_id=blog_id, blog_name=blog_name)
                for blog_id, blog_name in (zip(category.blog_ids, category.blog_names))
            ]
        )

    async def list(
        self,
        limit: int,
        offset: int,
        category_name: Optional[str] = None,
        approved: Optional[bool] = True,
        sort_order: SortOrder = SortOrder.ascending,
        sort_by: SortCategoryBy = SortCategoryBy.date_created,
    ) -> Union[List[CategoryReadList], int]:
        """Get listed categories based - either all or based on category_name or approved
        Args:
            limit [int]: up to how many results per page
            offset [int]: how many records should be skipped
            category_name (Optional[str], optional): Name of the category. Defaults to None.
            approved (Optional[bool], approved): If the categories should be approved. Defaults to True.
        Raises:
            BlogNotFound: raised if no blog matching criteria exists
            PaginationLimitSurpassed: raised if limit was suprassed
        Returns:
            List[BlogRead]: List of blogs matching users criteria
        """
        # Check limit
        if limit > 20:
            raise PaginationLimitSurpassed()

        # Create query
        q_pag, q_all = get_listed_categories_query(
            limit=limit,
            offset=offset,
            category_name=category_name,
            approved=approved,
            sort_order=sort_order,
            sort_by=sort_by,
        )
        # Execute queries with and without limit
        category_result = await self.db_session.exec(q_pag)
        all_result = await self.db_session.exec(q_all)
        categories = category_result.fetchall()
        total = all_result.fetchall()

        return categories, len(total)

async def get_category_service(session: AsyncSession = Depends(get_session)):
    yield CategoryService(session)

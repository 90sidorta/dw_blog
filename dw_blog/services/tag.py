from typing import Optional, List
from datetime import datetime
from uuid import UUID

from fastapi import Depends, HTTPException, status
from sqlmodel import Session, select
from sqlmodel.ext.asyncio.session import AsyncSession

from dw_blog.db.db import get_session
from dw_blog.models.tag import TagRead, Tag
from dw_blog.db.db import get_session
from dw_blog.utils.auth import check_if_admin
from dw_blog.models.auth import AuthUser
from dw_blog.services.user import UserService


class TagService:
    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.user_service = UserService(db_session)

    async def create(
        self,
        current_user: AuthUser,
        name: str,
    ) -> TagRead:
        user = await self.user_service.get(
            user_id=str(current_user["user_id"])
        )
        is_admin = check_if_admin(user.user_type)

        try:
            tag = Tag(
                text=name,
                date_created=datetime.now(),
                date_modified=datetime.now(),
            )
            self.db_session.add(tag)
            await self.db_session.commit()
            await self.db_session.refresh(tag)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to add tag!",
            )

        return tag

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

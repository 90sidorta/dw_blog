from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import Depends, HTTPException, status
from sqlmodel import Session, select
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import selectinload

from dw_blog.db.db import get_session
from dw_blog.schemas.auth import AuthUser
from dw_blog.exceptions.post import PostNotFound
from dw_blog.models.post import Post
from dw_blog.schemas.post import PostRead
from dw_blog.services.user import UserService
from dw_blog.utils.auth import check_if_admin


class PostService:
    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.user_service = UserService(db_session)

    async def create(
        self,
        current_user: AuthUser,
        text: str,
    ) -> PostRead:
        user = await self.user_service.get(user_id=str(current_user["user_id"]))
        is_author = check_if_admin(user.user_type)

        try:
            post = Post(
                text=text,
                date_created=datetime.now(),
                date_modified=datetime.now(),
                published=is_author,
                author_id=user.id,
                author_nickname=user.nickname,
            )
            self.db_session.add(post)
            await self.db_session.commit()
            await self.db_session.refresh(post)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to add post!",
            )

        return post

    async def get(
        self,
        post_id: UUID,
    ) -> PostRead:
        q = (
            select(Post)
            .options(
                selectinload(Post.authors),
                selectinload(Post.blog),
                selectinload(Post.tags),
            )
            .where(Post.id == post_id)
        )
        result = await self.db_session.exec(q)

        if not (post := result.first()):
            raise PostNotFound(post_id=post_id)

        return post

async def get_post_service(session: AsyncSession = Depends(get_session)):
    yield PostService(session)

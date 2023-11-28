from typing import Optional, List
from datetime import datetime
from uuid import UUID

from fastapi import Depends, HTTPException, status
from sqlmodel import Session, select
from sqlmodel.ext.asyncio.session import AsyncSession

from dw_blog.db.db import get_session
from dw_blog.models.post import Post, PostRead
from dw_blog.db.db import get_session
from dw_blog.utils.auth import check_if_admin
from dw_blog.models.auth import AuthUser
from dw_blog.services.user import UserService


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
        q = select(Post).where(Post.id == post_id)
        result = await self.db_session.exec(q)
        post = result.first()

        if post is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found!")

        return post

    # async def list(
    #     self,
    #     users_ids: Optional[List[UUID]],
    #     nickname: Optional[str],
    #     user_type: Optional[UserType],
    # ) -> List[UserRead]:
    #     q = select(User)
    #     if users_ids:
    #         q = q.where(User.id.in_(users_ids))
    #     if nickname:
    #         q = q.where(User.nickname.ilike(f"%{nickname}%"))
    #     if user_type:
    #         q = q.where(User.user_type == user_type)
    #     result = await self.db_session.exec(q)
    #     users = result.fetchall()
    #     return users

    # async def update(
    #     self,
    #     user_id: UUID,
    #     user_type: Optional[UserType] = None,
    #     description: Optional[str] = None,
    #     new_email: Optional[str] = None,
    #     confirm_email: Optional[str] = None,
    #     new_password: Optional[str] = None,
    #     confirm_password: Optional[str] = None,
    # ) -> UserRead:
    #     # Check if user exists
    #     self.get(user_id=user_id)
    #     # Get whole user object
    #     user_result = await self.db_session.exec(select(User).where(User.id == user_id))
    #     user = user_result.first()

    #     if user_type:
    #         user.user_type = user_type

    #     if description:
    #         user.description = description

    #     if new_email:
    #         if not confirm_email:
    #             raise HTTPException(
    #                 status_code=status.HTTP_400_BAD_REQUEST,
    #                 detail="New email should be confirmed!",
    #             )
    #         if new_email != confirm_email:
    #             raise HTTPException(
    #                 status_code=status.HTTP_400_BAD_REQUEST,
    #                 detail="Emails have to match!",
    #             )
    #         user.email = new_email

    #     if new_password:
    #         if not confirm_password:
    #             raise HTTPException(
    #                 status_code=status.HTTP_400_BAD_REQUEST,
    #                 detail="New password should be confirmed!",
    #             )
    #         if new_password != confirm_password:
    #             raise HTTPException(
    #                 status_code=status.HTTP_400_BAD_REQUEST,
    #                 detail="Passwords have to match!",
    #             )
    #         hasshed_password = get_password_hash(password=new_password)
    #         user.password = hasshed_password

    #     try:
    #         self.db_session.add(user)
    #         await self.db_session.commit()
    #     except Exception:
    #         raise HTTPException(
    #             status_code=status.HTTP_400_BAD_REQUEST,
    #             detail="Failed to update user!",
    #         )

    #     return user

    # async def delete(
    #     self,
    #     user_id: UUID,
    # ):
    #     user = self.get(user_id=user_id)
    #     try:
    #         self.db_session.delete(user)
    #         self.db_session.commit()
    #     except Exception:
    #         raise HTTPException(
    #             status_code=status.HTTP_404_NOT_FOUND,
    #             detail="Failed to delete user!",
    #         )


async def get_post_service(session: AsyncSession = Depends(get_session)):
    yield PostService(session)

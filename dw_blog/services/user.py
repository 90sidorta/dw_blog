from typing import List, Optional
from uuid import UUID

from fastapi import Depends, HTTPException, status
from sqlmodel import Session, select
from sqlmodel.ext.asyncio.session import AsyncSession

from dw_blog.db.db import get_session
from dw_blog.exceptions.user import UserNotFound
from dw_blog.schemas.auth import AuthUser
from dw_blog.schemas.common import UserType
from dw_blog.models.user import User
from dw_blog.schemas.user import UserRead
from dw_blog.utils.auth import check_user, get_password_hash


class UserService:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    async def create(
        self,
        nickname: str,
        user_type: UserType,
        email: str,
        password: str,
        confirm_password: str,
        confirm_email: str,
        description: Optional[str] = None,
    ) -> UserRead:
        if password != confirm_password:
            raise HTTPException(detail="Passwords do not match!", status_code=status.HTTP_400_BAD_REQUEST)
        if email != confirm_email:
            raise HTTPException(detail="Emails do not match!", status_code=status.HTTP_400_BAD_REQUEST)
        hasshed_password = get_password_hash(password=password)
        try:
            user = User(
                nickname=nickname, user_type=user_type, email=email, password=hasshed_password, description=description
            )
            self.db_session.add(user)
            await self.db_session.commit()
            await self.db_session.refresh(user)
        except Exception as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to add user!")
        return user

    async def get(
        self,
        user_id: Optional[UUID] = None,
        user_email: Optional[str] = None,
    ):
        q = select(User)
        if user_id:
            err_msg = f"User with id {user_id} not found"
            q = q.where(User.id == user_id)
        elif user_email:
            err_msg = f"User with email {user_email} not found"
            q = q.where(User.email == user_email)

        result = await self.db_session.execute(q)
        user = result.scalars().first()

        if user is None:
            raise UserNotFound(error_message=err_msg)

        return user

    async def list(
        self,
        users_ids: Optional[List[UUID]] = None,
        nickname: Optional[str] = None,
        user_type: Optional[UserType] = None,
    ) -> List[UserRead]:
        q = select(User)
        if users_ids:
            q = q.where(User.id.in_(users_ids))
        if nickname:
            q = q.where(User.nickname.ilike(f"%{nickname}%"))
        if user_type:
            q = q.where(User.user_type == user_type)
        result = await self.db_session.exec(q)
        users = result.fetchall()
        return users

    async def update(
        self,
        user_id: UUID,
        current_user: AuthUser,
        user_type: Optional[UserType] = None,
        description: Optional[str] = None,
        new_email: Optional[str] = None,
        confirm_email: Optional[str] = None,
        new_password: Optional[str] = None,
        confirm_password: Optional[str] = None,
    ) -> UserRead:
        # Check if user exists
        user = await self.get(user_id=user_id)
        # Chek user permissions
        check_user(
            user_id=str(user_id),
            current_user_id=str(current_user["user_id"]),
            user_type=user.user_type,
        )

        if user_type:
            user.user_type = user_type

        if description:
            user.description = description

        if new_email:
            if not confirm_email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="New email should be confirmed!",
                )
            if new_email != confirm_email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Emails have to match!",
                )
            user.email = new_email

        if new_password:
            if not confirm_password:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="New password should be confirmed!",
                )
            if new_password != confirm_password:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Passwords have to match!",
                )
            hasshed_password = get_password_hash(password=new_password)
            user.password = hasshed_password

        try:
            self.db_session.add(user)
            await self.db_session.commit()
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to update user!",
            )

        return user

    async def delete(
        self,
        user_id: UUID,
        current_user: AuthUser,
    ):
        # Check if user exists
        user = await self.get(user_id=user_id)
        # Chek user permissions
        check_user(
            user_id=str(user_id),
            current_user_id=str(current_user["user_id"]),
            user_type=user.user_type,
        )

        try:
            self.db_session.delete(user)
            self.db_session.commit()
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Failed to delete user!",
            )


async def get_user_service(session: AsyncSession = Depends(get_session)):
    yield UserService(session)

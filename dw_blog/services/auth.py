from typing import Optional, List
from datetime import datetime
from uuid import UUID

from fastapi import Depends, HTTPException, status
from sqlmodel import Session, select
from sqlmodel.ext.asyncio.session import AsyncSession

from dw_blog.db.db import get_session
from dw_blog.models.post import Post, PostRead
from dw_blog.db.db import get_session
from dw_blog.utils.auth import verify_password, create_access_token
from dw_blog.services.user import UserService
from dw_blog.models.auth import TokenType


class AuthService:
    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.user_service = UserService(db_session)

    async def login(
        self,
        username: str,
        password: str,
    ):
        user = await self.user_service.get(user_email=username)
        if not verify_password(
            plain_password=password,
            hashed_password=user.password
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials!",
            )
        token = create_access_token(
            user_id=user.id,
            user_type=user.user_type,
        )
        return {
            "access_token": token,
            "token_type": TokenType.bearer,
        }

    async def test(self):
        pass

async def get_auth_service(session: AsyncSession = Depends(get_session)):
    yield AuthService(session)

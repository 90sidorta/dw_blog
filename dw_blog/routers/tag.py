from uuid import UUID
from typing import Optional, List

from fastapi import APIRouter, Depends, status, Query

from dw_blog.models.tag import TagCreate, TagRead
from dw_blog.services.post import PostService, get_post_service
from dw_blog.utils.auth import get_current_user
from dw_blog.models.auth import AuthUser

router = APIRouter()


@router.post(
    "",
    response_model=PostRead,
    status_code=status.HTTP_201_CREATED,
)
async def add_post(
    request: PostCreate,
    post_service: PostService = Depends(get_post_service),
    current_user: AuthUser = Depends(get_current_user),
):
    return await post_service.create(
        current_user=current_user,
        **request.dict()
    )
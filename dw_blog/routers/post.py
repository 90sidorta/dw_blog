from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, status

from dw_blog.schemas.auth import AuthUser
from dw_blog.schemas.post import PostCreate, PostRead
from dw_blog.services.post import PostService, get_post_service
from dw_blog.utils.auth import get_current_user
from errors import RouteErrorHandler

router = APIRouter(route_class=RouteErrorHandler)


@router.post(
    "",
    # response_model=PostRead,
    status_code=status.HTTP_201_CREATED,
)
async def add_post(
    request: PostCreate,
    post_service: PostService = Depends(get_post_service),
    current_user: AuthUser = Depends(get_current_user),
):
    return await post_service.create(current_user=current_user, **request.dict())


@router.get(
    "/{post_id}",
    response_model=PostRead,
    status_code=status.HTTP_200_OK,
)
async def get_post(
    post_id: UUID,
    post_service: PostService = Depends(get_post_service),
):
    return await post_service.get(post_id=post_id)

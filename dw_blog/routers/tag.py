from uuid import UUID
from typing import Optional, List

from fastapi import APIRouter, Depends, status, Query

from dw_blog.models.common import ErrorModel
from dw_blog.models.tag import TagCreate, TagRead, TagCreate
from dw_blog.services.tag import TagService, get_tag_service
from dw_blog.utils.auth import get_current_user
from dw_blog.models.auth import AuthUser

router = APIRouter()


@router.post(
    "",
    response_model=TagRead,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": ErrorModel},
        401: {"model": ErrorModel},
        403: {"model": ErrorModel},
        422: {"model": ErrorModel},
    },
    summary="Create new tag",
    description="Create new tag for a given blog.",
)
async def add_post(
    request: TagCreate,
    tag_service: TagService = Depends(get_tag_service),
    current_user: AuthUser = Depends(get_current_user),
):
    return await tag_service.create(
        current_user=current_user,
        **request.dict()
    )


@router.get(
    "/{tag_id}",
    response_model=TagRead,
    status_code=status.HTTP_200_OK,
    responses={
        400: {"model": ErrorModel},
        401: {"model": ErrorModel},
        403: {"model": ErrorModel},
        404: {"model": ErrorModel},
    },
    summary="Get single tag",
    description="Get single tag data based on its id.",
)
async def get_blog(
    tag_id: UUID,
    tag_service: TagService = Depends(get_tag_service),
):
    return await tag_service.get(tag_id=tag_id)


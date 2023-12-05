from uuid import UUID
from typing import Optional

from fastapi import APIRouter, Depends, status

from dw_blog.models.auth import AuthUser
from dw_blog.models.common import ErrorModel
from dw_blog.models.tag import TagCreate, TagRead, TagUpdate, SortTagBy, ReadTagsPagination
from dw_blog.services.tag import TagService, get_tag_service
from dw_blog.utils.auth import get_current_user
from dw_blog.models.common import ErrorModel, Pagination, Sort, SortOrder

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
async def add_tag(
    request: TagCreate,
    tag_service: TagService = Depends(get_tag_service),
    current_user: AuthUser = Depends(get_current_user),
):
    return await tag_service.create(current_user=current_user, **request.dict())


@router.get(
    "",
    response_model=ReadTagsPagination,
    status_code=status.HTTP_200_OK,
    responses={
        400: {"model": ErrorModel},
        401: {"model": ErrorModel},
        403: {"model": ErrorModel},
    },
    summary="Get tags list",
    description="""Get list of tags. Can be subscribed tags of the specific user,
    list of tags according to count of subscriptions or list of tags of a specific
    blog according to number of subscriptions.
    """,
)
async def list_tags(
    limit: int = 10,
    offset: int = 0,
    user_id: Optional[UUID] = None,
    blog_id: Optional[UUID] = None,
    sort_order: SortOrder = SortOrder.ascending,
    sort_by: SortTagBy = SortTagBy.most_subscribers,
    tag_service: TagService = Depends(get_tag_service),
):
    data, total = await tag_service.list(
        limit=limit,
        offset=offset,
        user_id=user_id,
        blog_id=blog_id,
        sort_order=sort_order,
        sort_by=sort_by
    )
    return ReadTagsPagination(
        data=data,
        pagination=Pagination(
            total_records=total,
            limit=limit,
            offset=offset,
        ),
        sort=Sort(
            order=sort_order,
            prop=sort_by,
        ),
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
async def get_tag(
    tag_id: UUID,
    tag_service: TagService = Depends(get_tag_service),
):
    return await tag_service.get(tag_id=tag_id)


@router.patch(
    "/{tag_id}",
    response_model=TagRead,
    status_code=status.HTTP_200_OK,
    responses={
        400: {"model": ErrorModel},
        401: {"model": ErrorModel},
        403: {"model": ErrorModel},
        404: {"model": ErrorModel},
        422: {"model": ErrorModel},
    },
    summary="Update tag",
    description="Change name of a single tag.",
)
async def update_tag(
    tag_id: UUID,
    request: TagUpdate,
    current_user: AuthUser = Depends(get_current_user),
    tag_service: TagService = Depends(get_tag_service),
):
    return await tag_service.update(current_user=current_user, tag_id=tag_id, **request.dict())


@router.delete(
    "/{tag_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        400: {"model": ErrorModel},
        401: {"model": ErrorModel},
        403: {"model": ErrorModel},
        404: {"model": ErrorModel},
    },
    summary="Delete tag",
    description="Allows authors and admin to delete tag.",
)
async def delete_blog(
    tag_id: UUID,
    current_user: AuthUser = Depends(get_current_user),
    tag_service: TagService = Depends(get_tag_service),
):
    await tag_service.delete(
        blog_id=tag_id,
        current_user=current_user,
    )
    return

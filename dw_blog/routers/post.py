from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from dw_blog.schemas.auth import AuthUser
from dw_blog.schemas.common import Pagination, Sort, SortOrder
from dw_blog.schemas.post import PostCreate, PostRead, ReadBlogsPagination, SortPostBy, PostUpdate
from dw_blog.services.post import PostService, get_post_service
from dw_blog.utils.auth import get_current_user
from errors import RouteErrorHandler

router = APIRouter(route_class=RouteErrorHandler)


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


@router.get(
    "/",
    response_model=ReadBlogsPagination,
    status_code=status.HTTP_200_OK,
)
async def list_posts(
    limit: int = 10,
    offset: int = 0,
    published: bool = True,
    blog_id: Optional[UUID] = None,
    authors_ids: Optional[List[UUID]] = Query(None),
    tags_ids: Optional[List[UUID]] = Query(None),
    title_search: Optional[str] = None,
    body_search: Optional[str] = None,
    sort_order: SortOrder = SortOrder.ascending, 
    sort_by: SortPostBy = SortPostBy.date_created,
    post_service: PostService = Depends(get_post_service),
):
    data, total = await post_service.list(
        limit=limit,
        offset=offset,
        published=published,
        blog_id=blog_id,
        authors_ids=authors_ids,
        tags_ids=tags_ids,
        title_search=title_search,
        body_search=body_search,
        sort_order=sort_order,
        sort_by=sort_by,
    )

    return ReadBlogsPagination(
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


@router.patch(
    "/{post_id}",
    response_model=PostRead,
    status_code=status.HTTP_200_OK,
)
async def update_post(
    post_id: UUID,
    request: PostUpdate,
    post_service: PostService = Depends(get_post_service),
    current_user: AuthUser = Depends(get_current_user),
):
    return await post_service.update(
        post_id=post_id,
        current_user=current_user,
        **request.dict(),
    )


@router.post(
    "/{post_id}/like",
    response_model=PostRead,
    status_code=status.HTTP_200_OK,
)
async def like_post(
    post_id: UUID,
    post_service: PostService = Depends(get_post_service),
    current_user: AuthUser = Depends(get_current_user),
):
    return await post_service.like(post_id=post_id, current_user=current_user)


@router.post(
    "/{post_id}/unlike",
    response_model=PostRead,
    status_code=status.HTTP_200_OK,
)
async def unlike_post(
    post_id: UUID,
    post_service: PostService = Depends(get_post_service),
    current_user: AuthUser = Depends(get_current_user),
):
    return await post_service.unlike(post_id=post_id, current_user=current_user)


@router.delete(
    "/{post_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_post(
    post_id: UUID,
    post_service: PostService = Depends(get_post_service),
    current_user: AuthUser = Depends(get_current_user),
):
    await post_service.delete(post_id=post_id, current_user=current_user)

from uuid import UUID
from typing import Optional, List

from fastapi import APIRouter, Depends, status

from dw_blog.models.common import ErrorModel
from dw_blog.models.blog import BlogCreate, BlogRead, BlogUpdate
from dw_blog.services.blog import BlogService, get_blog_service
from dw_blog.utils.auth import get_current_user
from dw_blog.models.auth import AuthUser
from errors import RouteErrorHandler

router = APIRouter(route_class=RouteErrorHandler)


@router.post(
    "",
    response_model=BlogRead,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": ErrorModel},
        401: {"model": ErrorModel},
        403: {"model": ErrorModel},
        422: {"model": ErrorModel},
    },
    summary="Create new blog",
    description="Create new blog with creating user as an author.",
)
async def add_blog(
    request: BlogCreate,
    blog_service: BlogService = Depends(get_blog_service),
    current_user: AuthUser = Depends(get_current_user),
):
    return await blog_service.create(
        current_user=current_user,
        **request.dict()
    )


@router.get(
    "/{blog_id}",
    response_model=BlogRead,
    status_code=status.HTTP_200_OK,
    responses={
        400: {"model": ErrorModel},
        401: {"model": ErrorModel},
        403: {"model": ErrorModel},
        404: {"model": ErrorModel},
    },
    summary="Get single blog",
    description="Get single blog data with author information.",
)
async def get_blog(
    blog_id: UUID,
    blog_service: BlogService = Depends(get_blog_service),
):
    return await blog_service.get(blog_id=blog_id)


@router.get(
    "",
    response_model=List[BlogRead],
    status_code=status.HTTP_200_OK,
    responses={
        400: {"model": ErrorModel},
        401: {"model": ErrorModel},
        404: {"model": ErrorModel},
    },
    summary="Get list of blogs",
    description="""Get list of blogs with authors information.
    Blogs can be searched on the basis of authors names and blog name.
    """,
)
async def list_blogs(
    limit: int = 10,
    offset: int = 0,
    blog_name: Optional[str] = None,
    blog_service: BlogService = Depends(get_blog_service),
):
    return await blog_service.list(
        limit=limit,
        offset=offset,
        blog_name=blog_name,
    )


@router.post(
    "/{blog_id}/add_authors",
    response_model=BlogRead,
    status_code=status.HTTP_200_OK,
    responses={
        400: {"model": ErrorModel},
        401: {"model": ErrorModel},
        404: {"model": ErrorModel},
        422: {"model": ErrorModel},
    },
    summary="Add users as authors",
    description="Add upt to five users to a blog as authors.",
)
async def add_blog_authors(
    blog_id: UUID,
    add_author_ids: List[UUID],
    current_user: AuthUser = Depends(get_current_user),
    blog_service: BlogService = Depends(get_blog_service),
):
    return await blog_service.add_author_to_blog(
        blog_id=blog_id,
        current_user=current_user,
        add_author_ids=add_author_ids,
    )


@router.post(
    "/{blog_id}/remove_author",
    response_model=BlogRead,
    status_code=status.HTTP_200_OK,
    responses={
        400: {"model": ErrorModel},
        401: {"model": ErrorModel},
        403: {"model": ErrorModel},
        404: {"model": ErrorModel},
        422: {"model": ErrorModel},
    },
    summary="Remove users as authors",
    description="Remove authors from a blog (until one is left).",
)
async def remove_blog_authors(
    blog_id: UUID,
    remove_author_id: UUID,
    current_user: AuthUser = Depends(get_current_user),
    blog_service: BlogService = Depends(get_blog_service),
):
    return await blog_service.remove_author_from_blog(
        blog_id=blog_id,
        current_user=current_user,
        remove_author_id=remove_author_id,
    )


@router.patch(
    "/{blog_id}",
    response_model=BlogRead,
    status_code=status.HTTP_200_OK,
    responses={
        400: {"model": ErrorModel},
        401: {"model": ErrorModel},
        403: {"model": ErrorModel},
        404: {"model": ErrorModel},
        422: {"model": ErrorModel},
    },
    summary="Update blog",
    description="Allows authors and admin to update blogs name.",
)
async def update_blog(
    blog_id: UUID,
    request: BlogUpdate,
    current_user: AuthUser = Depends(get_current_user),
    blog_service: BlogService = Depends(get_blog_service),
):
    return await blog_service.update(
        blog_id=blog_id,
        current_user=current_user,
        **request.dict(),
    )


@router.delete(
    "/{blog_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        400: {"model": ErrorModel},
        401: {"model": ErrorModel},
        403: {"model": ErrorModel},
        404: {"model": ErrorModel},
    },
    summary="Delete blog",
    description="Allows authors and admin to delete blog.",
)
async def delete_blog(
    blog_id: UUID,
    current_user: AuthUser = Depends(get_current_user),
    blog_service: BlogService = Depends(get_blog_service),
):
    await blog_service.delete(
        blog_id=blog_id,
        current_user=current_user,
    )
    return

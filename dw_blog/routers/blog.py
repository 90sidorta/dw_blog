from uuid import UUID
from typing import Optional, List

from fastapi import APIRouter, Depends, status, Query

from dw_blog.models.blog import BlogCreate, BlogRead, BlogUpdate
from dw_blog.services.blog import BlogService, get_blog_service
from dw_blog.utils.auth import get_current_user
from dw_blog.models.auth import AuthUser

router = APIRouter()


@router.post(
    "",
    response_model=BlogRead,
    status_code=status.HTTP_201_CREATED,
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
)
async def list_blogs(
    author_name: Optional[str] = None,
    blog_name: Optional[str] = None, 
    blog_service: BlogService = Depends(get_blog_service),
):
    return await blog_service.list(
        author_name=author_name,
        blog_name=blog_name,
    )


@router.post(
    "/{blog_id}/add_authors",
    response_model=BlogRead,
    status_code=status.HTTP_200_OK,
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

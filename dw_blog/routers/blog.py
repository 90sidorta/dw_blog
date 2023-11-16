from uuid import UUID
from typing import Optional, List

from fastapi import APIRouter, Depends, status, Query

from dw_blog.models.blog import BlogCreate, BlogRead
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

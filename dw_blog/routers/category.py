from uuid import UUID

from fastapi import APIRouter, Depends, status

from dw_blog.models.auth import AuthUser
from dw_blog.models.common import ErrorModel
from dw_blog.models.category import CategoryCreate, CategoryRead
from dw_blog.services.category import CategoryService, get_category_service
from dw_blog.utils.auth import get_current_user

router = APIRouter()


@router.post(
    "",
    response_model=CategoryRead,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": ErrorModel},
        401: {"model": ErrorModel},
        403: {"model": ErrorModel},
        422: {"model": ErrorModel},
    },
    summary="Create new category",
    description="Creates new category.",
)
async def add_category(
    request: CategoryCreate,
    category_service: CategoryService = Depends(get_category_service),
    current_user: AuthUser = Depends(get_current_user),
):
    return await category_service.create(current_user=current_user, **request.dict())


@router.get(
    "/{category_id}",
    # response_model=CategoryRead,
    status_code=status.HTTP_200_OK,
    responses={
        400: {"model": ErrorModel},
        401: {"model": ErrorModel},
        403: {"model": ErrorModel},
        404: {"model": ErrorModel},
    },
    summary="Get single category",
    description="Get single category data with blogs, based on its id.",
)
async def get_category(
    category_id: UUID,
    category_service: CategoryService = Depends(get_category_service),
):
    return await category_service.get(category_id=category_id)

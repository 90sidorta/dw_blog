from uuid import UUID
from typing import Optional

from fastapi import APIRouter, Depends, status

from dw_blog.models.auth import AuthUser
from dw_blog.models.common import ErrorModel, Pagination, Sort, SortOrder
from dw_blog.models.category import CategoryCreate, CategoryRead, SortCategoryBy, ReadCategoriesPagination
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
    response_model=CategoryRead,
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


@router.get(
    "",
    # response_model=ReadBlogsPagination,
    status_code=status.HTTP_200_OK,
    responses={
        400: {"model": ErrorModel},
        401: {"model": ErrorModel},
        404: {"model": ErrorModel},
    },
    summary="Get list of categories",
    description="""Get list of categories with blog information.
    Categories can be searched on the basis of their name, popularity
    of blogs (subscribers and likers) and number of blogs.
    """,
)
async def list_categories(
    limit: int = 10,
    offset: int = 0,
    category_name: Optional[str] = None,
    approved: Optional[bool] = True,
    sort_order: SortOrder = SortOrder.descending,
    sort_by: SortCategoryBy = SortCategoryBy.blogs_with_most_likes,
    category_service: CategoryService = Depends(get_category_service),
):
    listed_categories, total = await category_service.list(
        limit=limit,
        offset=offset,
        category_name=category_name,
        approved=approved,
        sort_order=sort_order,
        sort_by=sort_by,
    )
    for cat in listed_categories:
        print("++++++++++++")
        print(cat)
        print("++++++++++++")
    # return ReadCategoriesPagination(
    #     data=listed_categories,
    #     pagination=Pagination(
    #         total_records=total,
    #         limit=limit,
    #         offset=offset,
    #     ),
    #     sort=Sort(
    #         order=sort_order,
    #         prop=sort_by,
    #     ),
    # )
    return True
from uuid import UUID
from typing import Optional, List

from fastapi import APIRouter, Depends, status, Query

from dw_blog.models.post import PostCreate, PostRead, PostUpdate, PostDelete
from dw_blog.services.post import PostService, get_post_service
from dw_blog.utils.auth import get_current_user
from dw_blog.models.auth import AuthUser

router = APIRouter()


@router.post(
    "",
    response_model=PostRead,
    status_code=status.HTTP_201_CREATED,
)
async def add_user(
    request: PostCreate,
    post_service: PostService = Depends(get_post_service),
    current_user: AuthUser = Depends(get_current_user),
):
    return await post_service.create(
        current_user=current_user,
        **request.dict()
    )


# @router.get(
#     "/{user_id}",
#     response_model=UserRead,
#     status_code=status.HTTP_200_OK,
# )
# async def get_user(
#     user_id: UUID,
#     example_service: UserService = Depends(get_user_service),
# ):
#     return await example_service.get(user_id=user_id)


# @router.get(
#     "",
#     response_model=List[UserRead],
#     status_code=status.HTTP_200_OK,
# )
# async def list_users(
#     users_ids: Optional[List[UUID]] = Query(None),
#     nickname: Optional[str] = None,
#     user_type: Optional[UserType] = None,
#     example_service: UserService = Depends(get_user_service),
# ):
#     return await example_service.list(
#         users_ids=users_ids,
#         nickname=nickname,
#         user_type=user_type
#     )


# @router.patch(
#     "/{user_id}",
#     response_model=UserRead,
#     status_code=status.HTTP_200_OK,
# )
# async def update_user(
#     user_id: UUID,
#     request: UserUpdate,
#     example_service: UserService = Depends(get_user_service),
# ):
#     return await example_service.update(user_id, **request.dict())

# @router.delete(
#     "",
#     status_code=status.HTTP_204_NO_CONTENT,
# )
# async def delete_user(
#     user_id: UUID,
#     example_service: UserService = Depends(get_user_service),
# ):
#     await example_service.delete(user_id=user_id)
#     return

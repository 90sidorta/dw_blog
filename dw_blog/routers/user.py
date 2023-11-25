from uuid import UUID
from typing import Optional, List

from fastapi import APIRouter, Depends, status, Query

from dw_blog.models.user import User, UserCreate, UserRead, UserUpdate, UserdDelete
from dw_blog.models.common import UserType
from dw_blog.services.user import UserService, get_user_service
from dw_blog.utils.auth import get_current_user
from dw_blog.models.auth import AuthUser

router = APIRouter()


@router.post(
    "",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
)
async def add_user(
    request: UserCreate,
    user_service: UserService = Depends(get_user_service),
):
    return await user_service.create(**request.dict())


@router.get(
    "/{user_id}",
    response_model=UserRead,
    status_code=status.HTTP_200_OK,
)
async def get_user(
    user_id: UUID,
    user_service: UserService = Depends(get_user_service),
):
    user = await user_service.get(user_id=user_id)
    return UserRead(**user.__dict__)


@router.get(
    "",
    response_model=List[UserRead],
    status_code=status.HTTP_200_OK,
)
async def list_users(
    users_ids: Optional[List[UUID]] = Query(None),
    nickname: Optional[str] = None,
    user_type: Optional[UserType] = None,
    user_service: UserService = Depends(get_user_service),
):
    return await user_service.list(
        users_ids=users_ids,
        nickname=nickname,
        user_type=user_type
    )


@router.patch(
    "/{user_id}",
    response_model=UserRead,
    status_code=status.HTTP_200_OK,
)
async def update_user(
    user_id: UUID,
    request: UserUpdate,
    user_service: UserService = Depends(get_user_service),
    current_user: AuthUser = Depends(get_current_user),
):
    return await user_service.update(
        user_id=user_id,
        current_user=current_user,
        **request.dict(),
    )


@router.delete(
    "",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_user(
    user_id: UserdDelete,
    user_service: UserService = Depends(get_user_service),
    current_user: AuthUser = Depends(get_current_user),
):
    await user_service.delete(
        user_id=user_id,
        current_user=current_user,
    )
    return

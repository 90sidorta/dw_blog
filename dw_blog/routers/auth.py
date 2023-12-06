from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from dw_blog.schemas.auth import Token
from dw_blog.services.auth import AuthService, get_auth_service

router = APIRouter()


@router.post(
    "/token",
    response_model=Token,
    status_code=status.HTTP_200_OK,
)
async def login(
    request: Annotated[OAuth2PasswordRequestForm, Depends()],
    auth_service: AuthService = Depends(get_auth_service),
):
    return await auth_service.login(
        username=request.username,
        password=request.password,
    )

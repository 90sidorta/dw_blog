import pytest

from httpx import AsyncClient
from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import status

from tests.factories import ADMIN_TOKEN, ADMIN_ID
from dw_blog.models.common import UserType


@pytest.mark.asyncio
async def test__get_user_200(
    async_client: AsyncClient,
    add_admin_user,
):
    response = await async_client.get(
        f"/users/{ADMIN_ID}",
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["user_type"] == UserType.admin.value
    assert response.json()["id"] == ADMIN_ID

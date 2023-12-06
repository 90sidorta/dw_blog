import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from dw_blog.schemas.common import UserType
from tests.factories import ADMIN_ID, ADMIN_TOKEN


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

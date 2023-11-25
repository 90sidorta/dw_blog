import pytest

from httpx import AsyncClient
from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import status

from tests.factories import ADMIN_TOKEN

@pytest.mark.asyncio


async def test__add_blog_200(
    async_client: AsyncClient,
    async_session: AsyncSession,
    user_token,
):
    admin_token = user_token["access_token"]
    blog_name = "Blog test name"
    print(user_token)

    response = await async_client.post(
        f"/blogs",
        json={"name": blog_name},
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["name"] == blog_name

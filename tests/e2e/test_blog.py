import pytest

from httpx import AsyncClient
from fastapi import status

from tests.factories import ADMIN_EMAIL

@pytest.mark.asyncio


async def test__add_blog_200(
    async_client: AsyncClient,
    add_admin_user,
    access_token,
):
    blog_name = "Blog test name"

    response = await async_client.post(
        f"/blogs",
        json={"name": blog_name},
        headers={"Authorization": f"Bearer {access_token}"}
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["name"] == blog_name

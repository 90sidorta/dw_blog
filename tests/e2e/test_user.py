import pytest

from httpx import AsyncClient
from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import status

from tests.factories import ADMIN_TOKEN, ADMIN_ID

@pytest.mark.asyncio


async def test__get_user_200(
    async_client: AsyncClient,
    async_session: AsyncSession,
):
    response = await async_client.get(
        f"/users/{ADMIN_ID}",
    )

    assert response.status_code == status.HTTP_200_OK
    # assert response.json()["name"] == blog_name

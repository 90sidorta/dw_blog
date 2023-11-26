import uuid
import pytest

from httpx import AsyncClient
from fastapi import status

from tests.factories import ADMIN_EMAIL, ADMIN_ID
from tests.conftest import _add_blog, _add_author_to_blog

@pytest.mark.asyncio


async def test__add_blog_200(
    async_client: AsyncClient,
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


async def test__add_blog_422_short_name(
    async_client: AsyncClient,
    access_token,
):
    blog_name = "Bl"

    response = await async_client.post(
        f"/blogs",
        json={"name": blog_name},
        headers={"Authorization": f"Bearer {access_token}"}
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert response.json()["detail"] == "Validation error: ensure this value has at least 3 characters!"
    assert response.json()["location"] == "name"


async def test__add_blog_403_more_than_three_blogs(
    async_client: AsyncClient,
    async_session,
    access_token,
):
    blog_1 = await _add_blog(async_session)
    blog_2 = await _add_blog(async_session)
    blog_3 = await _add_blog(async_session)
    await _add_author_to_blog(async_session, user_id=ADMIN_ID, blog_id=blog_1.id)
    await _add_author_to_blog(async_session, user_id=ADMIN_ID, blog_id=blog_2.id)
    await _add_author_to_blog(async_session, user_id=ADMIN_ID, blog_id=blog_3.id)
    blog_name = "Blog test name"

    response = await async_client.post(
        f"/blogs",
        json={"name": blog_name},
        headers={"Authorization": f"Bearer {access_token}"}
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["detail"] == "User already has 3 blogs!"


async def test__get_blog_200(
    async_client: AsyncClient,
    async_session,
):
    blog_1 = await _add_blog(async_session, name="Test blog")

    response = await async_client.get(
        f"/blogs/{blog_1.id}",
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["name"] == blog_1.name


async def test__get_blog_404_nonexistent(
    async_client: AsyncClient,
    async_session,
):
    blog_1 = uuid.uuid4()

    response = await async_client.get(
        f"/blogs/{blog_1}",
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND

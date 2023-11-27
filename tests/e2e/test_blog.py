import uuid
import pytest
from datetime import datetime, timedelta

from httpx import AsyncClient
from fastapi import status

from tests.factories import ADMIN_ID
from tests.conftest import _add_blog, _add_author_to_blog, _add_user

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


async def test__list_blogs_400_limit_passed(
    async_client: AsyncClient,
    async_session,
):
    await _add_blog(async_session, name="Test blog1")
    await _add_blog(async_session, name="Test blog2")
    await _add_blog(async_session, name="Test blog3")

    response = await async_client.get(
        f"/blogs?limit=30",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "Pagination limit cannot be higher than 20!"


async def test__list_blogs_200(
    async_client: AsyncClient,
    async_session,
):
    current_datetime = datetime.now()
    await _add_blog(async_session, name="Test blog1", date_created=current_datetime - timedelta(days=1))
    await _add_blog(async_session, name="Test blog2", date_created=current_datetime - timedelta(days=2))
    await _add_blog(async_session, name="Test blog3", date_created=current_datetime - timedelta(days=3))

    response = await async_client.get(
        f"/blogs?limit=1&offset=1&sort_by=date_created&sort_order=ascending",
    )

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["data"]) == 1
    assert response.json()["pagination"]["total_records"] >= 3
    assert response.json()["sort"] == {"order": "ascending", "prop": "date_created"}


async def test__list_blogs_200_sort_date_created(
    async_client: AsyncClient,
    async_session,
):
    current_datetime = datetime.now()
    await _add_blog(async_session, name="Test blog1", date_created=current_datetime - timedelta(days=1))
    await _add_blog(async_session, name="Test blog2", date_created=current_datetime - timedelta(days=2))
    await _add_blog(async_session, name="Test blog3", date_created=current_datetime - timedelta(days=3))

    response_asc = await async_client.get(
        f"/blogs?limit=10&offset=0&sort_by=date_created&sort_order=ascending",
    )
    response_dsc = await async_client.get(
        f"/blogs?limit=10&offset=0&sort_by=date_created&sort_order=descending",
    )

    assert response_asc.status_code == status.HTTP_200_OK
    assert response_dsc.status_code == status.HTTP_200_OK
    order_asc = [blog for blog in response_asc.json()["data"]]
    order_dsc = [blog for blog in response_dsc.json()["data"]]
    assert order_asc != order_dsc


async def test__list_blogs_200_sort_name(
    async_client: AsyncClient,
    async_session,
):
    await _add_blog(async_session, name="aaa")
    await _add_blog(async_session, name="bbb")
    await _add_blog(async_session, name="ccc")

    response_asc = await async_client.get(
        f"/blogs?limit=10&offset=0&sort_by=name&sort_order=ascending",
    )
    response_dsc = await async_client.get(
        f"/blogs?limit=10&offset=0&sort_by=name&sort_order=descending",
    )

    assert response_asc.status_code == status.HTTP_200_OK
    assert response_dsc.status_code == status.HTTP_200_OK
    order_asc = [blog for blog in response_asc.json()["data"]]
    order_dsc = [blog for blog in response_dsc.json()["data"]]
    assert order_asc != order_dsc


async def test__list_blogs_200_search_name(
    async_client: AsyncClient,
    async_session,
):
    await _add_blog(async_session, name="aaa")
    await _add_blog(async_session, name="aaabbb")
    await _add_blog(async_session, name="ccc")

    response = await async_client.get(
        f"/blogs?limit=10&offset=0&blog_name=aaa",
    )

    assert response.status_code == status.HTTP_200_OK
    blogs = [blog["name"] for blog in response.json()["data"]]
    assert "ccc" not in blogs


async def test__list_blogs_200_search_author(
    async_client: AsyncClient,
    async_session,
):
    user_1 = await _add_user(async_session, nickname="User1")
    user_2 = await _add_user(async_session, nickname="User2")
    await _add_blog(async_session, name="First", authors=[user_1])
    await _add_blog(async_session, name="Second", authors=[user_1])
    await _add_blog(async_session, name="Third", authors=[user_2])

    response = await async_client.get(
        f"/blogs?limit=10&offset=0&author_id={user_1.id}",
    )

    assert response.status_code == status.HTTP_200_OK
    blogs = [blog["name"] for blog in response.json()["data"]]
    assert "Third" not in blogs


async def test__list_blogs_200_search_name_nonexist(
    async_client: AsyncClient,
    async_session,
):
    await _add_blog(async_session, name="aaa")
    await _add_blog(async_session, name="aaabbb")
    await _add_blog(async_session, name="ccc")

    response = await async_client.get(
        f"/blogs?limit=10&offset=0&blog_name=zzz",
    )

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["data"]) == 0


async def test__list_blogs_200_search_author_nonexist(
    async_client: AsyncClient,
    async_session,
):
    user_1 = await _add_user(async_session, nickname="User1")
    user_2 = await _add_user(async_session, nickname="User2")
    await _add_blog(async_session, name="First", authors=[user_1])
    await _add_blog(async_session, name="Second", authors=[user_1])
    await _add_blog(async_session, name="Third", authors=[user_1])

    response = await async_client.get(
        f"/blogs?limit=10&offset=0&author_id={user_2.id}",
    )

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["data"]) == 0


async def test__add_blog_authors_200(
    async_client: AsyncClient,
    access_token,
    async_session,
):
    user_1 = await _add_user(async_session, nickname="User1")
    blog_1 = await _add_blog(async_session, name="First")

    response = await async_client.post(
        f"/blogs/{blog_1.id}/add_authors",
        json=[f"{user_1.id}"],
        headers={"Authorization": f"Bearer {access_token}"}
    )

    assert response.status_code == status.HTTP_200_OK
    authors = [author["nickname"] for author in response.json()["authors"]]
    assert "User1" in authors


async def test__add_blog_authors_400_already_five_authors(
    async_client: AsyncClient,
    access_token,
    async_session,
):
    user_1 = await _add_user(async_session, nickname="User1")
    user_2 = await _add_user(async_session, nickname="User2")
    user_3 = await _add_user(async_session, nickname="User3")
    user_4 = await _add_user(async_session, nickname="User4")
    user_5 = await _add_user(async_session, nickname="User5")
    user_6 = await _add_user(async_session, nickname="User6")
    blog_1 = await _add_blog(
        async_session,
        name="First",
        authors=[
            user_1, user_2, user_3, user_4, user_5
        ]
    )

    response = await async_client.post(
        f"/blogs/{blog_1.id}/add_authors",
        json=[f"{user_6.id}"],
        headers={"Authorization": f"Bearer {access_token}"}
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == 'Blog can only have 5 authors!'


# add_blog_authors
# - add existing user to a blog users has 3 already
# - add nonexisting users to a blog error
# - add existing users to a nonexisting blog error
# - add already added user to a blog
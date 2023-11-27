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
    assert response.json()["detail"] == f"User {ADMIN_ID} already has 3 blogs!"


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
):
    blog_1 = uuid.uuid4()

    response = await async_client.get(
        f"/blogs/{blog_1}",
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == f"Blog {blog_1} not found!"


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
    user_1 = await _add_user(async_session, nickname="UserOne")
    user_2 = await _add_user(async_session, nickname="UserTwo")
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
    user_1 = await _add_user(async_session)
    blog_1 = await _add_blog(async_session)

    response = await async_client.post(
        f"/blogs/{blog_1.id}/add_authors",
        json=[f"{user_1.id}"],
        headers={"Authorization": f"Bearer {access_token}"}
    )

    assert response.status_code == status.HTTP_200_OK
    authors = [author["nickname"] for author in response.json()["authors"]]
    assert user_1.nickname in authors


async def test__add_blog_authors_400(
    async_client: AsyncClient,
    access_token,
    async_session,
):
    user_1 = await _add_user(async_session)
    blog_1 = await _add_blog(async_session, authors=[user_1])

    response = await async_client.post(
        f"/blogs/{blog_1.id}/add_authors",
        json=[f"{user_1.id}"],
        headers={"Authorization": f"Bearer {access_token}"}
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert response.json()["detail"][0]["status_code"] == status.HTTP_403_FORBIDDEN
    assert response.json()["detail"][0]["detail"][0] == f"User {user_1.id} is already an author!"


async def test__add_blog_authors_403_not_your_blog(
    async_client: AsyncClient,
    other_user_access_token,
    async_session,
):
    user_1 = await _add_user(async_session)
    blog_1 = await _add_blog(async_session)

    response = await async_client.post(
        f"/blogs/{blog_1.id}/add_authors",
        json=[f"{user_1.id}"],
        headers={"Authorization": f"Bearer {other_user_access_token}"}
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["detail"] == f"Blog {blog_1.id} does not belong to you!"


async def test__add_blog_authors_400_already_five_authors(
    async_client: AsyncClient,
    access_token,
    async_session,
):
    user_1 = await _add_user(async_session)
    user_2 = await _add_user(async_session)
    user_3 = await _add_user(async_session)
    user_4 = await _add_user(async_session)
    user_5 = await _add_user(async_session)
    user_6 = await _add_user(async_session)
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
    assert response.json()["detail"] == f'Blog {blog_1.id} can only have 5 authors!'


async def test__add_blog_authors_422_already_three_blogs(
    async_client: AsyncClient,
    access_token,
    async_session,
):
    user_1 = await _add_user(async_session, name="more_than_3")
    blog_1 = await _add_blog(async_session, authors=[user_1])
    blog_2 = await _add_blog(async_session, authors=[user_1])
    blog_3 = await _add_blog(async_session, authors=[user_1])
    blog_4 = await _add_blog(async_session)

    response = await async_client.post(
        f"/blogs/{blog_4.id}/add_authors",
        json=[f"{user_1.id}"],
        headers={"Authorization": f"Bearer {access_token}"}
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert response.json()["detail"][0]["status_code"] == status.HTTP_403_FORBIDDEN
    assert response.json()["detail"][0]["detail"][0] == f"User {user_1.id} already has 3 blogs!"


async def test__add_blog_authors_422_nonexisting_user(
    async_client: AsyncClient,
    access_token,
    async_session,
):
    user_1 = uuid.uuid4()
    blog_1 = await _add_blog(async_session)

    response = await async_client.post(
        f"/blogs/{blog_1.id}/add_authors",
        json=[f"{user_1}"],
        headers={"Authorization": f"Bearer {access_token}"}
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert response.json()["detail"][0]["status_code"] == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"][0]["detail"][0] == f"User with id {user_1} not found"


async def test__add_blog_authors_404_nonexisting_blog(
    async_client: AsyncClient,
    access_token,
    async_session,
):
    user_1 = await _add_user(async_session)
    user_2 = await _add_user(async_session)
    blog_1 = uuid.uuid4()

    response = await async_client.post(
        f"/blogs/{blog_1}/add_authors",
        json=[f"{user_1.id}", f"{user_2.id}"],
        headers={"Authorization": f"Bearer {access_token}"}
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == f"Blog {blog_1} not found!"


async def test__remove_blog_author_200(
    async_client: AsyncClient,
    access_token,
    async_session,
):
    user_1 = await _add_user(async_session)
    user_2 = await _add_user(async_session)
    blog_1 = await _add_blog(async_session, authors=[user_1, user_2])

    response = await async_client.post(
        f"/blogs/{blog_1.id}/remove_author?remove_author_id={user_2.id}",
        headers={"Authorization": f"Bearer {access_token}"}
    )

    assert response.status_code == status.HTTP_200_OK
    authors = [author["nickname"] for author in response.json()["authors"]]
    assert user_2.nickname not in authors


async def test__remove_blog_author_400_delete_last_author(
    async_client: AsyncClient,
    access_token,
    async_session,
):
    user_1 = await _add_user(async_session)
    blog_1 = await _add_blog(async_session, authors=[user_1])

    response = await async_client.post(
        f"/blogs/{blog_1.id}/remove_author?remove_author_id={user_1.id}",
        headers={"Authorization": f"Bearer {access_token}"}
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "Can't delete the only author!"


async def test__remove_blog_author_400_delete_user_who_is_not_author(
    async_client: AsyncClient,
    access_token,
    async_session,
):
    user_1 = await _add_user(async_session)
    user_2 = await _add_user(async_session)
    blog_1 = await _add_blog(async_session, authors=[user_1])

    response = await async_client.post(
        f"/blogs/{blog_1.id}/remove_author?remove_author_id={user_2.id}",
        headers={"Authorization": f"Bearer {access_token}"}
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == f"User {user_2.id} is not an author of blog {blog_1.id}!"


async def test__remove_blog_author_403_not_your_blog(
    async_client: AsyncClient,
    other_user_access_token,
    async_session,
):
    user_1 = await _add_user(async_session)
    user_2 = await _add_user(async_session)
    blog_1 = await _add_blog(async_session, authors=[user_1, user_2])

    response = await async_client.post(
        f"/blogs/{blog_1.id}/remove_author?remove_author_id={user_2.id}",
        headers={"Authorization": f"Bearer {other_user_access_token}"}
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["detail"] == f"Blog {blog_1.id} does not belong to you!"


async def test__remove_blog_author_422_nonexisting_user(
    async_client: AsyncClient,
    access_token,
    async_session,
):
    user_1 = uuid.uuid4()
    blog_1 = await _add_blog(async_session)

    response = await async_client.post(
        f"/blogs/{blog_1.id}/remove_author?remove_author_id={user_1}",
        headers={"Authorization": f"Bearer {access_token}"}
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


async def test__remove_blog_author_404_nonexisting_blog(
    async_client: AsyncClient,
    access_token,
    async_session,
):
    user_1 = await _add_user(async_session)
    blog_1 = uuid.uuid4()

    response = await async_client.post(
        f"/blogs/{blog_1}/remove_author?remove_author_id={user_1.id}",
        headers={"Authorization": f"Bearer {access_token}"}
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == f"Blog {blog_1} not found!"




# ===add_blog_subscription===
# ===remove_blog_subscription===
# ===add_blog_like===
# ===remove_blog_like===
# ===update_blog===
# ===delete_blog===
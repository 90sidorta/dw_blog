import uuid
from datetime import datetime, timedelta

import pytest
from fastapi import status
from httpx import AsyncClient

from tests.conftest import (_add_author_to_blog, _add_blog,
                            _add_likers_to_blog, _add_subscriber_to_blog,
                            _add_user, _add_category)
from tests.factories import ADMIN_ID


@pytest.mark.asyncio
async def test__add_blog_200(
    async_client: AsyncClient,
    async_session,
    access_token,
):
    cat_1 = await _add_category(async_session)
    payload={"name": "Newest blog!", "categories_id": [str(cat_1.id)]}

    response = await async_client.post(
        f"/blogs", json=payload, headers={"Authorization": f"Bearer {access_token}"}
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["name"] == payload["name"]


async def test__add_blog_422_short_name(
    async_client: AsyncClient,
    async_session,
    access_token,
):
    cat_1 = await _add_category(async_session)
    payload={"name": "Bl", "categories_id": [str(cat_1.id)]}

    response = await async_client.post(
        f"/blogs", json=payload, headers={"Authorization": f"Bearer {access_token}"}
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert response.json()["detail"] == "Validation error: ensure this value has at least 3 characters!"
    assert response.json()["location"] == "name"


async def test__add_blog_403_more_than_three_blogs(
    async_client: AsyncClient,
    async_session,
    access_token,
):
    cat_1 = await _add_category(async_session)
    payload={"name": "Blog test name", "categories_id": [str(cat_1.id)]}
    blog_1 = await _add_blog(async_session)
    blog_2 = await _add_blog(async_session)
    blog_3 = await _add_blog(async_session)
    await _add_author_to_blog(async_session, user_id=ADMIN_ID, blog_id=blog_1.id)
    await _add_author_to_blog(async_session, user_id=ADMIN_ID, blog_id=blog_2.id)
    await _add_author_to_blog(async_session, user_id=ADMIN_ID, blog_id=blog_3.id)

    response = await async_client.post(
        f"/blogs", json=payload, headers={"Authorization": f"Bearer {access_token}"}
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


async def test__list_blogs_200_sort_subscribers(
    async_client: AsyncClient,
    async_session,
):
    user_1 = await _add_user(async_session)
    user_2 = await _add_user(async_session)
    user_3 = await _add_user(async_session)
    user_4 = await _add_user(async_session)
    await _add_blog(async_session, name="Test blog1", subscribers=[user_1, user_2, user_3, user_4])
    await _add_blog(async_session, name="Test blog2", subscribers=[user_1, user_2, user_3])
    await _add_blog(async_session, name="Test blog3", subscribers=[user_1, user_2])

    response_asc = await async_client.get(
        f"/blogs?limit=10&offset=0&sort_by=subscribers&sort_order=ascending",
    )
    response_dsc = await async_client.get(
        f"/blogs?limit=10&offset=0&sort_by=subscribers&sort_order=descending",
    )

    assert response_asc.status_code == status.HTTP_200_OK
    assert response_dsc.status_code == status.HTTP_200_OK
    order_asc = [blog for blog in response_asc.json()["data"]]
    order_dsc = [blog for blog in response_dsc.json()["data"]]
    assert order_asc != order_dsc


async def test__list_blogs_200_sort_likers(
    async_client: AsyncClient,
    async_session,
):
    user_1 = await _add_user(async_session)
    user_2 = await _add_user(async_session)
    user_3 = await _add_user(async_session)
    user_4 = await _add_user(async_session)
    await _add_blog(async_session, name="Test blog1", likers=[user_1, user_2, user_3, user_4])
    await _add_blog(async_session, name="Test blog2", likers=[user_1, user_2, user_3])
    await _add_blog(async_session, name="Test blog3", likers=[user_1, user_2])

    response_asc = await async_client.get(
        f"/blogs?limit=10&offset=0&sort_by=likers&sort_order=ascending",
    )
    response_dsc = await async_client.get(
        f"/blogs?limit=10&offset=0&sort_by=likers&sort_order=descending",
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


async def test__list_blogs_200_search_categories_ids(
    async_client: AsyncClient,
    async_session,
):
    cat_1 = await _add_category(async_session, name="ListCat1")
    cat_2 = await _add_category(async_session, name="ListCat2")
    cat_3 = await _add_category(async_session, name="ListCat3")
    await _add_blog(async_session, name="aaa", categories=[cat_1, cat_2])
    await _add_blog(async_session, name="aaabbb", categories=[cat_3])
    await _add_blog(async_session, name="ccc", categories=[cat_1, cat_2])

    response = await async_client.get(
        f"/blogs?limit=10&offset=0&categories_ids={cat_1.id}&categories_ids={cat_2.id}",
    )

    assert response.status_code == status.HTTP_200_OK
    blogs = [blog["name"] for blog in response.json()["data"]]
    assert "aaabbb" not in blogs


async def test__list_blogs_200_search_active_only(
    async_client: AsyncClient,
    async_session,
):
    await _add_blog(async_session, name="active_only_aaa", archived=False)
    await _add_blog(async_session, name="active_only_bbb", archived=False)
    await _add_blog(async_session, name="active_only_ccc", archived=True)

    response = await async_client.get(
        f"/blogs?limit=10&offset=0&archived=false&blog_name=active_only",
    )

    assert response.status_code == status.HTTP_200_OK
    blogs = [blog["name"] for blog in response.json()["data"]]
    assert "active_only_ccc" not in blogs


async def test__list_blogs_200_search_archived_only(
    async_client: AsyncClient,
    async_session,
):
    await _add_blog(async_session, name="archive_only_aaa", archived=True)
    await _add_blog(async_session, name="archive_only_bbb", archived=True)
    await _add_blog(async_session, name="archive_only_ccc", archived=False)

    response = await async_client.get(
        f"/blogs?limit=10&offset=0&archived=true&blog_name=archive_",
    )

    assert response.status_code == status.HTTP_200_OK
    blogs = [blog["name"] for blog in response.json()["data"]]
    assert "archive_only_ccc" not in blogs


async def test__list_blogs_200_search_active_archived(
    async_client: AsyncClient,
    async_session,
):
    await _add_blog(async_session, name="both_aaa", archived=False)
    await _add_blog(async_session, name="both_bbb", archived=False)
    await _add_blog(async_session, name="both_ccc", archived=True)

    response = await async_client.get(
        f"/blogs?limit=10&offset=0&blog_name=both_",
    )

    assert response.status_code == status.HTTP_200_OK
    blogs = [blog["name"] for blog in response.json()["data"]]
    assert "both_aaa" in blogs
    assert "both_bbb" in blogs
    assert "both_ccc" in blogs


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
        f"/blogs/{blog_1.id}/add_authors", json=[f"{user_1.id}"], headers={"Authorization": f"Bearer {access_token}"}
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
        f"/blogs/{blog_1.id}/add_authors", json=[f"{user_1.id}"], headers={"Authorization": f"Bearer {access_token}"}
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert response.json()["detail"][0]["status_code"] == status.HTTP_403_FORBIDDEN
    assert response.json()["detail"][0]["detail"] == f"User {user_1.id} is already an author!"


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
        headers={"Authorization": f"Bearer {other_user_access_token}"},
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["detail"] == "To perform author addition you need either to be an admin or author of the blog!"


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
    blog_1 = await _add_blog(async_session, name="First", authors=[user_1, user_2, user_3, user_4, user_5])

    response = await async_client.post(
        f"/blogs/{blog_1.id}/add_authors", json=[f"{user_6.id}"], headers={"Authorization": f"Bearer {access_token}"}
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == f"Blog {blog_1.id} can only have 5 authors!"


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
        f"/blogs/{blog_4.id}/add_authors", json=[f"{user_1.id}"], headers={"Authorization": f"Bearer {access_token}"}
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert response.json()["detail"][0]["status_code"] == status.HTTP_403_FORBIDDEN
    assert response.json()["detail"][0]["detail"] == f"User {user_1.id} already has 3 blogs!"


async def test__add_blog_authors_422_nonexisting_user(
    async_client: AsyncClient,
    access_token,
    async_session,
):
    user_1 = uuid.uuid4()
    blog_1 = await _add_blog(async_session)

    response = await async_client.post(
        f"/blogs/{blog_1.id}/add_authors", json=[f"{user_1}"], headers={"Authorization": f"Bearer {access_token}"}
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert response.json()["detail"][0]["status_code"] == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"][0]["detail"] == f"User with id {user_1} not found"


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
        headers={"Authorization": f"Bearer {access_token}"},
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
        headers={"Authorization": f"Bearer {access_token}"},
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
        headers={"Authorization": f"Bearer {access_token}"},
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
        headers={"Authorization": f"Bearer {access_token}"},
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
        headers={"Authorization": f"Bearer {other_user_access_token}"},
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["detail"] == "To perform author removal you need either to be an admin or author of the blog!"


async def test__remove_blog_author_422_nonexisting_user(
    async_client: AsyncClient,
    access_token,
    async_session,
):
    user_1 = uuid.uuid4()
    blog_1 = await _add_blog(async_session)

    response = await async_client.post(
        f"/blogs/{blog_1.id}/remove_author?remove_author_id={user_1}",
        headers={"Authorization": f"Bearer {access_token}"},
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
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == f"Blog {blog_1} not found!"


async def test__add_blog_subscription_200(
    async_client: AsyncClient,
    access_token,
    async_session,
):
    blog_1 = await _add_blog(async_session)

    response = await async_client.post(
        f"/blogs/{blog_1.id}/subscribe", headers={"Authorization": f"Bearer {access_token}"}
    )

    assert response.status_code == status.HTTP_200_OK
    subscribers = [subscriber["subscriber_id"] for subscriber in response.json()["subscribers"]]
    assert ADMIN_ID in subscribers


async def test__add_blog_subscription_400_already_subscribed(
    async_client: AsyncClient,
    access_token,
    async_session,
):
    blog_1 = await _add_blog(async_session)
    await _add_subscriber_to_blog(async_session, user_id=ADMIN_ID, blog_id=blog_1.id)

    response = await async_client.post(
        f"/blogs/{blog_1.id}/subscribe", headers={"Authorization": f"Bearer {access_token}"}
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == f"You already subscribed blog {blog_1.id}!"


async def test__add_blog_subscription_404_blog_nonexistent(
    async_client: AsyncClient,
    access_token,
):
    blog_1 = uuid.uuid4()

    response = await async_client.post(
        f"/blogs/{blog_1}/subscribe", headers={"Authorization": f"Bearer {access_token}"}
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == f"Blog {blog_1} not found!"


async def test__add_blog_subscription_400_blog_archived(
    async_client: AsyncClient,
    access_token,
    async_session,
):
    blog_1 = await _add_blog(async_session, archived=True)

    response = await async_client.post(
        f"/blogs/{blog_1.id}/subscribe", headers={"Authorization": f"Bearer {access_token}"}
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == f"Blog {blog_1.id} is archived!"


async def test__remove_blog_subscription_200(
    async_client: AsyncClient,
    access_token,
    async_session,
):
    blog_1 = await _add_blog(async_session)
    await _add_subscriber_to_blog(async_session, user_id=ADMIN_ID, blog_id=blog_1.id)

    response = await async_client.post(
        f"/blogs/{blog_1.id}/unsubscribe", headers={"Authorization": f"Bearer {access_token}"}
    )

    assert response.status_code == status.HTTP_200_OK
    subscribers = [subscriber["subscriber_id"] for subscriber in response.json()["subscribers"]]
    assert ADMIN_ID not in subscribers


async def test__remove_blog_subscription_400_not_subscribed(
    async_client: AsyncClient,
    access_token,
    async_session,
):
    blog_1 = await _add_blog(async_session)

    response = await async_client.post(
        f"/blogs/{blog_1.id}/unsubscribe", headers={"Authorization": f"Bearer {access_token}"}
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == f"You don't subscribe blog {blog_1.id}!"


async def test__remove_blog_subscription_404_blog_nonexistent(
    async_client: AsyncClient,
    access_token,
):
    blog_1 = uuid.uuid4()

    response = await async_client.post(
        f"/blogs/{blog_1}/unsubscribe", headers={"Authorization": f"Bearer {access_token}"}
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == f"Blog {blog_1} not found!"


async def test__add_blog_like_200(
    async_client: AsyncClient,
    access_token,
    async_session,
):
    blog_1 = await _add_blog(async_session)

    response = await async_client.post(f"/blogs/{blog_1.id}/like", headers={"Authorization": f"Bearer {access_token}"})

    assert response.status_code == status.HTTP_200_OK
    likers = [liker["liker_id"] for liker in response.json()["likers"]]
    assert ADMIN_ID in likers


async def test__add_blog_like_400_already_liked(
    async_client: AsyncClient,
    access_token,
    async_session,
):
    blog_1 = await _add_blog(async_session)
    await _add_likers_to_blog(async_session, user_id=ADMIN_ID, blog_id=blog_1.id)

    response = await async_client.post(f"/blogs/{blog_1.id}/like", headers={"Authorization": f"Bearer {access_token}"})

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == f"You already liked blog {blog_1.id}!"


async def test__add_blog_like_404_blog_nonexistent(
    async_client: AsyncClient,
    access_token,
):
    blog_1 = uuid.uuid4()

    response = await async_client.post(f"/blogs/{blog_1}/like", headers={"Authorization": f"Bearer {access_token}"})

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == f"Blog {blog_1} not found!"


async def test__add_blog_like_400_blog_archived(
    async_client: AsyncClient,
    access_token,
    async_session,
):
    blog_1 = await _add_blog(async_session, archived=True)

    response = await async_client.post(f"/blogs/{blog_1.id}/like", headers={"Authorization": f"Bearer {access_token}"})

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == f"Blog {blog_1.id} is archived!"


async def test__remove_blog_like_200(
    async_client: AsyncClient,
    access_token,
    async_session,
):
    blog_1 = await _add_blog(async_session)
    await _add_likers_to_blog(async_session, user_id=ADMIN_ID, blog_id=blog_1.id)

    response = await async_client.post(
        f"/blogs/{blog_1.id}/unlike", headers={"Authorization": f"Bearer {access_token}"}
    )

    assert response.status_code == status.HTTP_200_OK
    likers = [liker["liker_id"] for liker in response.json()["likers"]]
    assert ADMIN_ID not in likers


async def test__remove_blog_like_400_not_liked(
    async_client: AsyncClient,
    access_token,
    async_session,
):
    blog_1 = await _add_blog(async_session)

    response = await async_client.post(
        f"/blogs/{blog_1.id}/unlike", headers={"Authorization": f"Bearer {access_token}"}
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == f"You did not like blog {blog_1.id}!"


async def test__remove_blog_like_404_blog_nonexistent(
    async_client: AsyncClient,
    access_token,
):
    blog_1 = uuid.uuid4()

    response = await async_client.post(f"/blogs/{blog_1}/unlike", headers={"Authorization": f"Bearer {access_token}"})

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == f"Blog {blog_1} not found!"


async def test__update_blog_200_name(
    async_client: AsyncClient,
    access_token,
    async_session,
):
    blog_1 = await _add_blog(async_session)
    await _add_author_to_blog(async_session, user_id=ADMIN_ID, blog_id=blog_1.id)
    payload = {"name": "Completely new name"}

    response = await async_client.patch(
        f"/blogs/{blog_1.id}", headers={"Authorization": f"Bearer {access_token}"},
        json=payload,
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["name"] == payload["name"]


async def test__update_blog_200_add_category(
    async_client: AsyncClient,
    access_token,
    async_session,
):
    cat_1 = await _add_category(async_session, name="category1")
    cat_2 = await _add_category(async_session, name="category2")
    blog_1 = await _add_blog(async_session, categories=[cat_1])
    payload = {"add_categories_id": [f"{cat_2.id}"]}

    response = await async_client.patch(
        f"/blogs/{blog_1.id}", headers={"Authorization": f"Bearer {access_token}"},
        json=payload,
    )

    assert response.status_code == status.HTTP_200_OK
    assert cat_1.name in response.json()["categories_name"]
    assert cat_2.name in response.json()["categories_name"]


async def test__update_blog_400_add_category_already_added(
    async_client: AsyncClient,
    access_token,
    async_session,
):
    cat_1 = await _add_category(async_session, name="category11")
    blog_1 = await _add_blog(async_session, categories=[cat_1])
    payload = {"add_categories_id": [f"{cat_1.id}"]}

    response = await async_client.patch(
        f"/blogs/{blog_1.id}", headers={"Authorization": f"Bearer {access_token}"},
        json=payload,
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == f"Blog {blog_1.id} already belongs to category {cat_1.id}!"


async def test__update_blog_400_add_category_more_than_3(
    async_client: AsyncClient,
    access_token,
    async_session,
):
    cat_1 = await _add_category(async_session, name="category111")
    cat_2 = await _add_category(async_session, name="category222")
    cat_3 = await _add_category(async_session, name="category333")
    cat_4 = await _add_category(async_session, name="category444")
    blog_1 = await _add_blog(async_session, categories=[cat_1, cat_2])
    payload = {"add_categories_id": [f"{cat_3.id}", f"{cat_4.id}"]}

    response = await async_client.patch(
        f"/blogs/{blog_1.id}", headers={"Authorization": f"Bearer {access_token}"},
        json=payload,
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == f"Blog {blog_1.id} already has 2 categories! Adding 2 would exceed the limit of three!"


async def test__update_blog_404_add_category_nonexistent(
    async_client: AsyncClient,
    access_token,
    async_session,
):
    cat_1 = await _add_category(async_session, name="category10")
    blog_1 = await _add_blog(async_session, categories=[cat_1])
    cat_2 = uuid.uuid4()
    payload = {"add_categories_id": [f"{cat_2}"]}

    response = await async_client.patch(
        f"/blogs/{blog_1.id}", headers={"Authorization": f"Bearer {access_token}"},
        json=payload,
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == f"Failed to fetch category {cat_2}!"


async def test__update_blog_200_remove_category(
    async_client: AsyncClient,
    access_token,
    async_session,
):
    cat_1 = await _add_category(async_session, name="category101")
    cat_2 = await _add_category(async_session, name="category202")
    blog_1 = await _add_blog(async_session, categories=[cat_1, cat_2])
    payload = {"remove_categories_id": [f"{cat_2.id}"]}

    response = await async_client.patch(
        f"/blogs/{blog_1.id}", headers={"Authorization": f"Bearer {access_token}"},
        json=payload,
    )

    assert response.status_code == status.HTTP_200_OK
    assert cat_1.name in response.json()["categories_name"]
    assert cat_2.name not in response.json()["categories_name"]


async def test__update_blog_400_remove_category_not_added(
    async_client: AsyncClient,
    access_token,
    async_session,
):
    cat_1 = await _add_category(async_session, name="category9")
    cat_2 = await _add_category(async_session, name="category8")
    blog_1 = await _add_blog(async_session, categories=[cat_1])
    payload = {"remove_categories_id": [f"{cat_2.id}"]}

    response = await async_client.patch(
        f"/blogs/{blog_1.id}", headers={"Authorization": f"Bearer {access_token}"},
        json=payload,
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == f"Blog {blog_1.id} does not belong to category {cat_2.id}!"


async def test__update_blog_404_remove_category_nonexistent(
    async_client: AsyncClient,
    access_token,
    async_session,
):
    cat_1 = await _add_category(async_session, name="category91")
    blog_1 = await _add_blog(async_session, categories=[cat_1])
    cat_2 = uuid.uuid4()
    payload = {"remove_categories_id": [f"{cat_2}"]}

    response = await async_client.patch(
        f"/blogs/{blog_1.id}", headers={"Authorization": f"Bearer {access_token}"},
        json=payload,
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == f"Failed to fetch category {cat_2}!"


async def test__update_blog_400_remove_all_categories(
    async_client: AsyncClient,
    access_token,
    async_session,
):
    cat_1 = await _add_category(async_session, name="category911")
    cat_2 = await _add_category(async_session, name="category922")
    blog_1 = await _add_blog(async_session, categories=[cat_1, cat_2])
    payload = {"remove_categories_id": [f"{cat_2.id}", f"{cat_1.id}"]}

    response = await async_client.patch(
        f"/blogs/{blog_1.id}", headers={"Authorization": f"Bearer {access_token}"},
        json=payload,
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == f"You can not delete all categories from blog {blog_1.id}!"


async def test__update_blog_422_name_too_short(
    async_client: AsyncClient,
    access_token,
    async_session,
):
    blog_1 = await _add_blog(async_session)
    await _add_author_to_blog(async_session, user_id=ADMIN_ID, blog_id=blog_1.id)
    payload = {"name": "a"}

    response = await async_client.patch(
        f"/blogs/{blog_1.id}", headers={"Authorization": f"Bearer {access_token}"},
        json=payload,
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert response.json()["detail"] == "Validation error: ensure this value has at least 3 characters!"
    assert response.json()["location"] == "name"


async def test__update_blog_200_deactivate(
    async_client: AsyncClient,
    access_token,
    async_session,
):
    blog_1 = await _add_blog(async_session)
    await _add_author_to_blog(async_session, user_id=ADMIN_ID, blog_id=blog_1.id)
    payload = {"archived": True}

    response = await async_client.patch(
        f"/blogs/{blog_1.id}", headers={"Authorization": f"Bearer {access_token}"},
        json=payload,
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["archived"] == payload["archived"]


async def test__update_blog_403_other_user_blog(
    async_client: AsyncClient,
    other_user_access_token,
    async_session,
):
    blog_1 = await _add_blog(async_session)
    payload = {"name": "Completely new name"}

    response = await async_client.patch(
        f"/blogs/{blog_1.id}", headers={"Authorization": f"Bearer {other_user_access_token}"},
        json=payload,
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["detail"] == "To perform blog update you need either to be an admin or author of the blog!"


async def test__update_blog_404_nonexistent_blog(
    async_client: AsyncClient,
    access_token,
):
    blog_1 = uuid.uuid4()
    payload = {"name": "Completely new name"}

    response = await async_client.patch(
        f"/blogs/{blog_1}", headers={"Authorization": f"Bearer {access_token}"},
        json=payload,
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == f"Blog {blog_1} not found!"


async def test__delete_blog_204(
    async_client: AsyncClient,
    access_token,
    async_session,
):
    blog_1 = await _add_blog(async_session)
    await _add_author_to_blog(async_session, user_id=ADMIN_ID, blog_id=blog_1.id)

    response = await async_client.delete(
        f"/blogs/{blog_1.id}", headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT


async def test__delete_blog_403_other_user_blog(
    async_client: AsyncClient,
    other_user_access_token,
    async_session,
):
    blog_1 = await _add_blog(async_session)

    response = await async_client.delete(
        f"/blogs/{blog_1.id}", headers={"Authorization": f"Bearer {other_user_access_token}"},
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["detail"] == "To perform blog deletion you need either to be an admin or author of the blog!"

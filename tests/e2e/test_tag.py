import uuid
from datetime import datetime, timedelta

import pytest
from fastapi import status
from httpx import AsyncClient

from tests.conftest import (_add_author_to_blog, _add_blog,
                            _add_likers_to_blog, _add_subscriber_to_blog,
                            _add_user, _add_category, _add_tag)
from tests.factories import ADMIN_ID


@pytest.mark.asyncio
async def test__add_tag_200(
    async_client: AsyncClient,
    async_session,
    access_token,
):
    blog_1 = await _add_blog(async_session)
    payload={"name": "#newest", "blog_id": str(blog_1.id)}

    response = await async_client.post(
        f"/tags",
        json=payload,
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["name"] == payload["name"]
    assert response.json()["blog_id"] == payload["blog_id"]


async def test__add_tag_404_blog_nonexistent(
    async_client: AsyncClient,
    access_token,
):
    blog_1 = uuid.uuid4()
    payload={"name": "#newest404", "blog_id": str(blog_1)}

    response = await async_client.post(
        f"/tags",
        json=payload,
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == f"Blog {blog_1} not found!"


async def test__add_tag_403_not_owner(
    async_client: AsyncClient,
     other_user_access_token,
    async_session,
):
    blog_1 = await _add_blog(async_session)
    payload={"name": "#newest403", "blog_id": str(blog_1.id)}

    response = await async_client.post(
        f"/tags",
        json=payload,
        headers={"Authorization": f"Bearer {other_user_access_token}"},
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["detail"] == f"To perform add tag you need either to be an admin or author of the blog!"


async def test__add_tag_422_invalid_name(
    async_client: AsyncClient,
    async_session,
    access_token,
):
    blog_1 = await _add_blog(async_session)
    payload={"name": "newest", "blog_id": str(blog_1.id)}

    response = await async_client.post(
        f"/tags",
        json=payload,
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert response.json()["detail"] == """Validation error: string does not match regex "#\w+"!"""


async def test__list_tags_200(
    async_client: AsyncClient,
    async_session,
    access_token,
):
    blog_1 = await _add_blog(async_session)
    blog_2 = await _add_blog(async_session)
    user_1 = await _add_user(async_session)
    user_2 = await _add_user(async_session)
    await _add_tag(async_session, name="#list_test_200", blog=blog_1, blog_id=blog_1.id, subscribers=[user_1, user_2])
    await _add_tag(async_session, name="#list_test_201", blog=blog_1, blog_id=blog_1.id, subscribers=[user_1])
    await _add_tag(async_session, name="#list_test_202", blog=blog_2, blog_id=blog_2.id, subscribers=[])

    response = await async_client.get(
        f"/tags?tag_name=list_test_20",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["data"]) == 3
    assert response.json()["pagination"] == {"total_records": 3, "limit": 10, "offset": 0}
    assert response.json()["sort"] == {"order": "ascending", "prop": "most_subscribers"}


async def test__list_tags_200_sort_most_subs(
    async_client: AsyncClient,
    async_session,
    access_token,
):
    blog_1 = await _add_blog(async_session)
    blog_2 = await _add_blog(async_session)
    user_1 = await _add_user(async_session)
    user_2 = await _add_user(async_session)
    await _add_tag(async_session, name="#most_subs_200", blog=blog_1, blog_id=blog_1.id, subscribers=[user_1, user_2])
    await _add_tag(async_session, name="#most_subs_201", blog=blog_1, blog_id=blog_1.id, subscribers=[user_1])
    await _add_tag(async_session, name="#most_subs_202", blog=blog_2, blog_id=blog_2.id, subscribers=[])

    response_asc = await async_client.get(
        f"/tags?tag_name=most_subs_20&sort_order=ascending&sort_by=most_subscribers",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    response_dsc = await async_client.get(
        f"/tags?tag_name=most_subs_20&sort_order=descending&sort_by=most_subscribers",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response_asc.status_code == status.HTTP_200_OK
    assert response_dsc.status_code == status.HTTP_200_OK
    order_asc = [tag for tag in response_asc.json()["data"]]
    order_dsc = [tag for tag in response_dsc.json()["data"]]
    assert order_asc != order_dsc


async def test__list_tags_200_sort_date_created(
    async_client: AsyncClient,
    async_session,
    access_token,
):
    current_datetime = datetime.now()
    blog_1 = await _add_blog(async_session)
    blog_2 = await _add_blog(async_session)
    await _add_tag(
        async_session,
        name="#date_created_200",
        blog=blog_1,
        blog_id=blog_1.id,
        date_created=current_datetime - timedelta(days=1),
    )
    await _add_tag(
        async_session,
        name="#date_created_201",
        blog=blog_1,
        blog_id=blog_1.id,
        date_created=current_datetime - timedelta(days=2),
    )
    await _add_tag(
        async_session,
        name="#date_created_202",
        blog=blog_2,
        blog_id=blog_2.id,
        date_created=current_datetime - timedelta(days=3),
    )

    response_asc = await async_client.get(
        f"/tags?tag_name=date_created_20&sort_order=ascending&sort_by=date_created",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    response_dsc = await async_client.get(
        f"/tags?tag_name=date_created_20&sort_order=descending&sort_by=date_created",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response_asc.status_code == status.HTTP_200_OK
    assert response_dsc.status_code == status.HTTP_200_OK
    order_asc = [tag for tag in response_asc.json()["data"]]
    order_dsc = [tag for tag in response_dsc.json()["data"]]
    assert order_asc != order_dsc


async def test__list_tags_200_filter_blog_id(
    async_client: AsyncClient,
    async_session,
    access_token,
):
    blog_1 = await _add_blog(async_session)
    blog_2 = await _add_blog(async_session)
    user_1 = await _add_user(async_session)
    user_2 = await _add_user(async_session)
    await _add_tag(async_session, name="#blog_id_200", blog=blog_1, blog_id=blog_1.id, subscribers=[user_1, user_2])
    await _add_tag(async_session, name="#blog_id_201", blog=blog_1, blog_id=blog_1.id, subscribers=[user_1])
    await _add_tag(async_session, name="#blog_id_202", blog=blog_2, blog_id=blog_2.id, subscribers=[])

    response = await async_client.get(
        f"/tags?tag_name=blog_id_20&blog_id={blog_1.id}",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["data"]) == 2


async def test__list_tags_200_filter_subscriber_id(
    async_client: AsyncClient,
    async_session,
    access_token,
):
    blog_1 = await _add_blog(async_session)
    blog_2 = await _add_blog(async_session)
    user_1 = await _add_user(async_session)
    user_2 = await _add_user(async_session)
    await _add_tag(async_session, name="#user_id_200", blog=blog_1, blog_id=blog_1.id, subscribers=[user_1, user_2])
    await _add_tag(async_session, name="#user_id_201", blog=blog_1, blog_id=blog_1.id, subscribers=[user_1])
    await _add_tag(async_session, name="#user_id_202", blog=blog_2, blog_id=blog_2.id, subscribers=[])

    response = await async_client.get(
        f"/tags?tag_name=user_id_20&user_id={user_1.id}",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["data"]) == 2


async def test__list_tags_400_filter_subscriber_id_blog_id(
    async_client: AsyncClient,
    async_session,
    access_token,
):
    blog_1 = await _add_blog(async_session)
    blog_2 = await _add_blog(async_session)
    user_1 = await _add_user(async_session)
    user_2 = await _add_user(async_session)
    await _add_tag(async_session, name="#both_id_200", blog=blog_1, blog_id=blog_1.id, subscribers=[user_1, user_2])
    await _add_tag(async_session, name="#both_id_201", blog=blog_1, blog_id=blog_1.id, subscribers=[user_1])
    await _add_tag(async_session, name="#both_id_202", blog=blog_2, blog_id=blog_2.id, subscribers=[])

    response = await async_client.get(
        f"/tags?tag_name=both_id_20&user_id={user_1.id}&blog_id={blog_1.id}",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "Tags can either be filtered by blog or by subscriber! Can not filter by both!"


# get_tag
# add_tag_subscription
# remove_tag_subscription
# update_tag
# delete_blog
import uuid
from datetime import datetime, timedelta

import pytest
from fastapi import status
from httpx import AsyncClient

from tests.conftest import (_add_blog,
                            _add_likers_to_blog,
                            _add_user,
                            _add_category)
from tests.factories import ADMIN_ID


@pytest.mark.asyncio
async def test__add_category_201_admin(
    async_client: AsyncClient,
    access_token,
):
    payload={"name": "Newest blog!"}

    response = await async_client.post(
        f"/categories", json=payload, headers={"Authorization": f"Bearer {access_token}"}
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["name"] == payload["name"]
    assert response.json()["approved"] == True


async def test__add_category_201_regular(
    async_client: AsyncClient,
    other_user_access_token,
):
    payload={"name": "Newest blog regular!"}

    response = await async_client.post(
        f"/categories", json=payload, headers={"Authorization": f"Bearer {other_user_access_token}"}
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["name"] == payload["name"]
    assert response.json()["approved"] == False


async def test__add_category_422(
    async_client: AsyncClient,
    access_token,
):
    payload={"name": "Newest blog!" * 50}

    response = await async_client.post(
        f"/categories", json=payload, headers={"Authorization": f"Bearer {access_token}"}
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert response.json()["detail"] == "Validation error: ensure this value has at most 500 characters!"
    assert response.json()["location"] == "name"


async def test__get_category_200(
    async_client: AsyncClient,
    access_token,
    async_session,
):
    cat_1 = await _add_category(async_session)

    response = await async_client.get(
        f"/categories/{cat_1.id}", headers={"Authorization": f"Bearer {access_token}"}
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["name"] == cat_1.name


async def test__get_category_404(
    async_client: AsyncClient,
    access_token,
):
    cat_1 = uuid.uuid4()

    response = await async_client.get(
        f"/categories/{cat_1}", headers={"Authorization": f"Bearer {access_token}"}
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == f"Failed to fetch category {cat_1}!"


async def test__list_categories_200_sort_by_date_created(
    async_client: AsyncClient,
    access_token,
    async_session,
):
    current_datetime = datetime.now()
    await _add_category(async_session, date_created=current_datetime - timedelta(days=1))
    await _add_category(async_session, date_created=current_datetime - timedelta(days=2))
    await _add_category(async_session, date_created=current_datetime - timedelta(days=3))
    await _add_category(async_session, date_created=current_datetime - timedelta(days=4))

    response_asc = await async_client.get(
        "/categories?sort_order=ascending&sort_by=date_created",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    response_dsc = await async_client.get(
        "/categories?sort_order=descending&sort_by=date_created",
        headers={"Authorization": f"Bearer {access_token}"}
    )

    assert response_asc.status_code == status.HTTP_200_OK
    assert response_dsc.status_code == status.HTTP_200_OK
    order_asc = [cat for cat in response_asc.json()["data"]]
    order_dsc = [cat for cat in response_dsc.json()["data"]]
    assert order_asc != order_dsc


async def test__list_categories_200_sort_by_name(
    async_client: AsyncClient,
    access_token,
    async_session,
):
    await _add_category(async_session, name="aaa")
    await _add_category(async_session, name="bbb")
    await _add_category(async_session, name="ccc")
    await _add_category(async_session, name="ddd")

    response_asc = await async_client.get(
        "/categories?sort_order=ascending&sort_by=name",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    response_dsc = await async_client.get(
        "/categories?sort_order=descending&sort_by=name",
        headers={"Authorization": f"Bearer {access_token}"}
    )

    assert response_asc.status_code == status.HTTP_200_OK
    assert response_dsc.status_code == status.HTTP_200_OK
    order_asc = [cat for cat in response_asc.json()["data"]]
    order_dsc = [cat for cat in response_dsc.json()["data"]]
    assert order_asc != order_dsc


async def test__list_categories_200_sort_by_blogs_count(
    async_client: AsyncClient,
    access_token,
    async_session,
):
    blog_1 = await _add_blog(async_session)
    blog_2 = await _add_blog(async_session)
    blog_3 = await _add_blog(async_session)
    blog_4 = await _add_blog(async_session)
    blog_5 = await _add_blog(async_session)
    blog_6 = await _add_blog(async_session)
    await _add_category(async_session, blogs=[blog_1, blog_2, blog_3])
    await _add_category(async_session, blogs=[blog_4, blog_5])
    await _add_category(async_session, blogs=[blog_6])
    await _add_category(async_session, blogs=[])


    response_asc = await async_client.get(
        "/categories?sort_order=ascending&sort_by=most_blogs",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    response_dsc = await async_client.get(
        "/categories?sort_order=descending&sort_by=most_blogs",
        headers={"Authorization": f"Bearer {access_token}"}
    )

    assert response_asc.status_code == status.HTTP_200_OK
    assert response_dsc.status_code == status.HTTP_200_OK
    order_asc = [cat for cat in response_asc.json()["data"]]
    order_dsc = [cat for cat in response_dsc.json()["data"]]
    assert order_asc != order_dsc


async def test__list_categories_200_sort_by_blog_likes_count(
    async_client: AsyncClient,
    access_token,
    async_session,
):
    user_1 = await _add_user(async_session)
    user_2 = await _add_user(async_session)
    blog_1 = await _add_blog(async_session, name="Test1", likers=[user_1, user_2])
    blog_2 = await _add_blog(async_session, name="Test2", likers=[])
    _add_likers_to_blog(async_session, user_id=ADMIN_ID, blog_id=blog_1.id)


    response_asc = await async_client.get(
        "/categories?sort_order=ascending&sort_by=blogs_with_most_likes",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    response_dsc = await async_client.get(
        "/categories?sort_order=descending&sort_by=blogs_with_most_likes",
        headers={"Authorization": f"Bearer {access_token}"}
    )

    assert response_asc.status_code == status.HTTP_200_OK
    assert response_dsc.status_code == status.HTTP_200_OK
    order_asc = [cat["name"] for cat in response_asc.json()["data"]]
    order_dsc = [cat["name"] for cat in response_dsc.json()["data"]]
    assert order_asc != order_dsc


async def test__list_categories_200_approved(
    async_client: AsyncClient,
    access_token,
    async_session,
):
    await _add_category(async_session, name="approved1",approved=True)
    await _add_category(async_session, name="approved2",approved=True)
    await _add_category(async_session, name="approved3",approved=False)
    await _add_category(async_session, name="approved4",approved=True)
    await _add_category(async_session, name="approved5",approved=False)

    response_true = await async_client.get(
        "/categories?approved=true&name=approved",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    response_false = await async_client.get(
        "/categories?approved=false&name=approved",
        headers={"Authorization": f"Bearer {access_token}"}
    )

    assert response_true.status_code == status.HTTP_200_OK
    assert response_false.status_code == status.HTTP_200_OK
    assert set([cat["approved"] for cat in response_true.json()["data"]]) == {True}
    assert set([cat["approved"] for cat in response_false.json()["data"]]) == {False}
    assert response_true.json()["sort"] == {"order": "descending", "prop": "blogs_with_most_likes"}


async def test__update_category_200(
    async_client: AsyncClient,
    access_token,
    async_session,
):
    cat_1 = await _add_category(async_session, name="before_change", approved=False)
    payload = {"name": "after_change", "approved": True}

    response = await async_client.patch(
        f"/categories/{cat_1.id}",
        json=payload,
        headers={"Authorization": f"Bearer {access_token}"}
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["name"] == payload["name"]
    assert response.json()["approved"] == payload["approved"]


async def test__update_category_404_nonexistent_category(
    async_client: AsyncClient,
    access_token,
):
    cat_1 = uuid.uuid4()
    payload = {"name": "after_change", "approved": True}

    response = await async_client.patch(
        f"/categories/{cat_1}",
        json=payload,
        headers={"Authorization": f"Bearer {access_token}"}
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == f"Failed to fetch category {cat_1}!"


async def test__update_category_400_invalid_name(
    async_client: AsyncClient,
    access_token,
    async_session,
):
    cat_1 = await _add_category(async_session, name="before_change", approved=False)
    payload = {"name": "af"}

    response = await async_client.patch(
        f"/categories/{cat_1.id}",
        json=payload,
        headers={"Authorization": f"Bearer {access_token}"}
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert response.json()["detail"] == "Validation error: ensure this value has at least 3 characters!"
    assert response.json()["location"] == "name"


async def test__update_category_403_other_user(
    async_client: AsyncClient,
    other_user_access_token,
    async_session,
):
    cat_1 = await _add_category(async_session, name="zxcxzczxczxcz", approved=False)
    payload = {"name": "zxcxzczx1czxcz"}

    response = await async_client.patch(
        f"/categories/{cat_1.id}",
        json=payload,
        headers={"Authorization": f"Bearer {other_user_access_token}"}
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["detail"] == "To perform category update you need admin status!"


async def test__delete_category_204(
    async_client: AsyncClient,
    access_token,
    async_session,
):
    cat_1 = await _add_category(async_session)

    response = await async_client.delete(
        f"/categories/{cat_1.id}",
        headers={"Authorization": f"Bearer {access_token}"}
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT


async def test__delete_category_404(
    async_client: AsyncClient,
    access_token,
):
    cat_1 = uuid.uuid4()

    response = await async_client.delete(
        f"/categories/{cat_1}",
        headers={"Authorization": f"Bearer {access_token}"}
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


async def test__delete_category_400_category_with_blogs(
    async_client: AsyncClient,
    access_token,
    async_session,
):
    cat_1 = await _add_category(async_session)
    blog_1 = await _add_blog(async_session, categories=[cat_1])

    response = await async_client.delete(
        f"/categories/{cat_1.id}",
        headers={"Authorization": f"Bearer {access_token}"}
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == f"Failed to delete category {cat_1.id}! It has associated blogs!"


async def test__delete_category_403_not_admin(
    async_client: AsyncClient,
    async_session,
    other_user_access_token,
):
    cat_1 = await _add_category(async_session)
    blog_1 = await _add_blog(async_session, categories=[cat_1])

    response = await async_client.delete(
        f"/categories/{cat_1.id}",
        headers={"Authorization": f"Bearer {other_user_access_token}"}
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["detail"] == "To perform category delete you need admin status!"

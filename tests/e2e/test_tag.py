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

# add_tag
# 404, blog not exist
# 403, not admin or owner of the blog
# 422, invalid tag name
# list_tags
# get_tag
# add_tag_subscription
# remove_tag_subscription
# update_tag
# delete_blog
# import uuid
# from datetime import datetime, timedelta
#
# import pytest
# from fastapi import status
# from httpx import AsyncClient
#
# from tests.conftest import (_add_blog,
#                             _add_likers_to_blog,
#                             _add_user,
#                             _add_category)
# from tests.factories import ADMIN_ID
#
#
# @pytest.mark.asyncio
# async def test__add_post_201(
#     async_client: AsyncClient,
#     access_token,
# ):
#     payload = {"name": "Newest blog!"}
#
#     response = await async_client.post(
#         f"/categories", json=payload, headers={"Authorization": f"Bearer {access_token}"}
#     )
#
#     assert response.status_code == status.HTTP_201_CREATED
#     assert response.json()["name"] == payload["name"]
#     assert response.json()["approved"] is True

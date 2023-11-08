import pytest
from httpx import AsyncClient
from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

@pytest.mark.asyncio

async def test__example(async_client: AsyncClient, async_session: AsyncSession):
    assert 1 == 1
    # clear_data(db_session)
    # project = _add_project(db_session)
    # payload = {
    #         "project_id": str(project.id),
    #         "name": "new category name",
    #         "development_type": DevelopmentType.EXPERIMENT.value,
    #         "position": 0,
    # }

    # response = await async_client.post(
    #     f"/api/categories",
    #     json=payload,
    #     headers={"Authorization": f"Bearer {OWNER_TOKEN}"}
    # )

    # assert response.status_code == status.HTTP_201_CREATED
    # assert response.json()["name"] == payload["name"]
    # assert response.json()["development_type"] == payload["development_type"]
    # assert response.json()["position"] == payload["position"]
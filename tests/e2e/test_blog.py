import pytest
from httpx import AsyncClient
from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

@pytest.mark.asyncio

async def test__example(async_client: AsyncClient, async_session: AsyncSession):
    assert 1 == 1
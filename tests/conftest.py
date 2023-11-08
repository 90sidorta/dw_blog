import asyncio
import os
import json
from typing import Generator

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlmodel import SQLModel

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from dw_blog.config import Settings
from main import app

settings = Settings()
db_url_test_sync = settings.DATABASE_URL_TEST_SYNC
db_url_test = settings.DATABASE_URL_TEST
root = settings.ROOT_DIR


@pytest.fixture(scope="session")
def event_loop(request) -> Generator:  # noqa: indirect usage
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def async_client():
    async with AsyncClient(
            app=app,
            base_url="http://testserver",
    ) as client:
        yield client


@pytest_asyncio.fixture(scope="function")
async def async_session() -> AsyncSession:
    async_engine = create_async_engine(db_url_test, echo=True, future=True)
    session = sessionmaker(
        async_engine, class_=AsyncSession, expire_on_commit=False
    )

    async with session() as s:
        async with async_engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)

        yield s

    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)

    await async_engine.dispose()


@pytest.fixture(scope="function")
def test_data() -> dict:
    path = os.getenv('PYTEST_CURRENT_TEST')
    path = os.path.join(*os.path.split(path)[:-1], "data", "data.json")

    if not os.path.exists(path):
        path = os.path.join("data", "data.json")

    with open(path, "r") as file:
        data = json.loads(file.read())

    return data

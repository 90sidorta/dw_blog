import asyncio
import os
import json
from typing import Generator

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlmodel import SQLModel
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import create_database, database_exists

from dw_blog.config import Settings
from tests.factories import UserFactory, ADMIN_ID, ADMIN_EMAIL
from main import app

settings = Settings()
db_url_test_sync = settings.DATABASE_URL_TEST_SYNC
db_url_test = settings.DATABASE_URL_TEST
root = settings.ROOT_DIR
async_engine = create_async_engine(db_url_test, echo=True, future=True)
sync_engine = create_engine(db_url_test_sync)

@pytest.fixture(scope="session")
def event_loop(request) -> Generator:  # noqa: indirect usage
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def async_client():
    async with AsyncClient(
            app=app,
            base_url="http://testserver",
    ) as client:
        yield client

@pytest.fixture(scope='session')
async def async_db_engine():
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    yield async_engine

    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def async_session(async_db_engine) -> AsyncSession:
    # Create test db if it does not exist
    if not database_exists(sync_engine.url):
        create_database(sync_engine.url)

    async_session = sessionmaker(
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
        bind=async_db_engine,
        class_=AsyncSession,
    )

    async with async_session() as session:
        await session.begin()

        yield session

        # Add admin user
        user = UserFactory(id=ADMIN_ID, email=ADMIN_EMAIL)
        session.add(user)
        await session.commit()

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


def _add_user(db_session, **kwargs):
    user = UserFactory(**kwargs)
    db_session.add(user)
    db_session.commit()
    return user

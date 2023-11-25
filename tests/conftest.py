import asyncio
from typing import Generator, AsyncGenerator

import pytest
from httpx import AsyncClient
from sqlmodel import SQLModel
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import create_database, database_exists

from dw_blog.config import Settings
from dw_blog.db.db import get_session
from tests.factories import UserFactory, ADMIN_ID, ADMIN_EMAIL
from dw_blog.models.user import User
from dw_blog.models.common import UserType
from main import app

settings = Settings()
db_url_test_sync = settings.DATABASE_URL_TEST_SYNC
db_url_test = settings.DATABASE_URL_TEST
root = settings.ROOT_DIR
async_engine = create_async_engine(db_url_test, echo=True, future=True)
sync_engine = create_engine(db_url_test_sync)


@pytest.fixture(
    params=[
        pytest.param(("asyncio", {"use_uvloop": True}), id="asyncio+uvloop"),
    ]
)
def anyio_backend(request):
    return request.param


@pytest.fixture(scope="session", autouse=True)
async def init_db():
    # Create test db if it does not exist
    if not database_exists(sync_engine.url):
        create_database(sync_engine.url)

    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    yield async_engine

    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)


@pytest.fixture
def async_session_maker() -> sessionmaker:
    engine_async = create_async_engine(db_url_test)
    return sessionmaker(engine_async, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture
async def async_session(async_session_maker) -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


@pytest.fixture
async def async_client(async_session) -> AsyncClient:
    async with AsyncClient(
        app=app,
        base_url="http://testserver",
    ) as async_client:
        app.dependency_overrides[get_session] = lambda: async_session

        yield async_client


@pytest.fixture(scope="session")
def event_loop() -> Generator:  # noqa: indirect usage
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def add_admin_user(async_session: AsyncSession) -> User:
    # Add admin user
    user = UserFactory(id=ADMIN_ID, email=ADMIN_EMAIL, user_type=UserType.admin)
    async_session.add(user)
    await async_session.commit()
    await async_session.refresh(user)
    return user


def _add_user(db_session, **kwargs):
    user = UserFactory(**kwargs)
    db_session.add(user)
    db_session.commit()
    return user

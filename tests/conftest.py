import asyncio
from uuid import UUID
from typing import Generator, AsyncGenerator

import pytest
from httpx import AsyncClient
from sqlmodel import SQLModel
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import create_database, database_exists

from dw_blog.config import Settings
from dw_blog.db.db import get_session
from tests.factories import UserFactory, ADMIN_ID, ADMIN_EMAIL, BlogFactory
from dw_blog.models.user import User
from dw_blog.models.common import UserType
from dw_blog.models.blog import BlogAuthors, BlogSubscribers, BlogLikes
from dw_blog.utils.auth import create_access_token
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
        exists = await session.get(User, ADMIN_ID)
        if not exists:
            user = UserFactory(
                id=ADMIN_ID,
                email=ADMIN_EMAIL,
                user_type=UserType.admin
            )
            session.add(user)
            await session.commit()
            await session.refresh(user)
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
async def access_token():
    return create_access_token(
        user_id=ADMIN_ID,
        user_type=UserType.admin,
    )


async def _add_user(db_session, **kwargs):
    user = UserFactory(**kwargs)
    db_session.add(user)
    await db_session.commit()
    return user


async def _add_blog(db_session, **kwargs):
    blog = BlogFactory(**kwargs)
    db_session.add(blog)
    await db_session.commit()
    return blog


async def _add_author_to_blog(db_session, user_id: UUID, blog_id: UUID):
    blog_author = BlogAuthors(blog_id=blog_id, author_id=user_id)
    db_session.add(blog_author)
    await db_session.commit()
    return blog_author


async def _add_subscriber_to_blog(db_session, user_id: UUID, blog_id: UUID):
    blog_subscriber = BlogSubscribers(blog_id=blog_id, subscriber_id=user_id)
    db_session.add(blog_subscriber)
    await db_session.commit()
    return blog_subscriber


async def _add_likers_to_blog(db_session, user_id: UUID, blog_id: UUID):
    blog_liker = BlogLikes(blog_id=blog_id, liker_id=user_id)
    db_session.add(blog_liker)
    await db_session.commit()
    return blog_liker


@pytest.fixture
async def other_user_access_token(async_session):
    other_user = await _add_user(async_session, user_type=UserType.regular)
    return create_access_token(
        user_id=other_user.id,
        user_type=UserType.regular,
    )

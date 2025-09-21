import uuid
from unittest.mock import patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from dao.base import Base


@pytest.fixture
def unique_name():
    return f"test_group_{uuid.uuid4().hex[:8]}"


@pytest.fixture(scope="function")
async def test_db_session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
    session = async_session()

    yield session

    await session.close()
    await engine.dispose()


@pytest.fixture(autouse=True)
async def mock_db_session(test_db_session):
    with patch('dao.group.get_session_or_create', return_value=test_db_session):
        with patch('dao.base.get_session_or_create', return_value=test_db_session):
            yield
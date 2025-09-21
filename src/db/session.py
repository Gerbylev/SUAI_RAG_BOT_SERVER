from contextvars import ContextVar
from typing import Optional

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_scoped_session,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import declarative_base

from utils.config import CONFIG

Base = declarative_base()

db_config = CONFIG.db

db_session_context: ContextVar[Optional[int]] = ContextVar("db_session_context", default=None)
engine = create_async_engine(url=f"postgresql+asyncpg://{db_config.username}:{db_config.password}@{db_config.host}:{db_config.port}/{db_config.database}")

session_factory = async_sessionmaker(bind=engine, autocommit=False, autoflush=False)


async def get_db_session():
    db_session = session_factory()
    try:
        yield db_session
    finally:
        await db_session.close()


def get_db_session_context() -> int:
    session_id = db_session_context.get()

    if not session_id:
        raise ValueError("Currently no session is available")

    return session_id


def set_db_session_context(*, session_id: Optional[int]) -> None:
    db_session_context.set(session_id)


AsyncScopedSession = async_scoped_session(
    session_factory=async_sessionmaker(bind=engine, autoflush=False, autocommit=False),
    scopefunc=get_db_session_context,
)


def get_current_session() -> AsyncSession:
    return AsyncScopedSession()


async def get_session_or_create() -> AsyncSession:
    try:
        return get_current_session()
    except ValueError:
        return session_factory()

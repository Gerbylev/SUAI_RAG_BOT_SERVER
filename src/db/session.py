from contextlib import asynccontextmanager
from contextvars import ContextVar
from typing import AsyncIterator, Optional

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
    """
    FastAPI dependency для создания новой БД сессии.
    Автоматически закрывает сессию после использования.

    Использование:
        @app.get("/endpoint")
        async def endpoint(session: AsyncSession = Depends(get_db_session)):
            ...
    """
    db_session = session_factory()
    try:
        yield db_session
    finally:
        await db_session.close()


def get_db_session_context() -> int:
    """
    Получает ID текущего контекста сессии.
    Используется внутри scoped session для разделения сессий по контекстам.

    Raises:
        ValueError: если контекст сессии не установлен
    """
    session_id = db_session_context.get()

    if not session_id:
        raise ValueError("Currently no session is available")

    return session_id


def set_db_session_context(*, session_id: Optional[int]) -> None:
    """
    Устанавливает ID контекста сессии.
    Используется декоратором @transactional для управления контекстом.

    Args:
        session_id: ID контекста сессии или None для сброса
    """
    db_session_context.set(session_id)


AsyncScopedSession = async_scoped_session(
    session_factory=async_sessionmaker(bind=engine, autoflush=False, autocommit=False),
    scopefunc=get_db_session_context,
)


def get_current_session() -> AsyncSession:
    """
    Получает текущую БД сессию из scoped контекста.

    ВАЖНО: Использовать только внутри @transactional декоратора!
    Вне транзакции вызовет ValueError.

    Returns:
        AsyncSession: текущая сессия из контекста

    Raises:
        ValueError: если вызвана вне @transactional контекста

    Использование:
        @transactional
        async def my_function():
            session = get_current_session()
            result = await session.execute(...)
    """
    return AsyncScopedSession()


def create_new_session() -> AsyncSession:
    """
    Создает новую БД сессию вне scoped контекста.

    ВАЖНО: Сессия НЕ управляется автоматически!
    Необходимо вручную закрывать через await session.close()

    Returns:
        AsyncSession: новая несвязанная сессия

    Использование:
        session = create_new_session()
        try:
            result = await session.execute(...)
            await session.commit()
        finally:
            await session.close()
    """
    return session_factory()


@asynccontextmanager
async def get_session() -> AsyncIterator[AsyncSession]:
    """
    УНИВЕРСАЛЬНЫЙ интерфейс получения БД сессии с автоматическим управлением.

    Автоматически определяет контекст:
    - Внутри @transactional: использует существующую сессию, НЕ закрывает её
    - Вне @transactional: создает новую сессию, автоматически закрывает при выходе

    Returns:
        AsyncIterator[AsyncSession]: async context manager с сессией

    Использование:
        # Работает внутри @transactional
        @transactional
        async def my_func():
            async with get_session() as session:
                await session.execute(...)

        # Работает и снаружи @transactional
        async def another_func():
            async with get_session() as session:
                await session.execute(...)
                await session.commit()  # не забыть commit если вне @transactional
    """
    try:
        # Пытаемся получить сессию из транзакционного контекста
        session = get_current_session()
        # Сессия управляется декоратором @transactional, не закрываем
        yield session
    except ValueError:
        # Контекста нет, создаем новую независимую сессию
        session = create_new_session()
        try:
            yield session
        finally:
            await session.close()

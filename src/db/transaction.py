import functools
from typing import Any, Awaitable, Callable

from utils.logger import get_logger

from .session import get_current_session, get_db_session_context

AsyncCallable = Callable[..., Awaitable]
logger = get_logger("Transaction")


def transactional(func: AsyncCallable) -> AsyncCallable:
    @functools.wraps(func)
    async def _wrapper(*args, **kwargs) -> Awaitable[Any]:
        try:
            db_session = get_current_session()

            if db_session.in_transaction():
                return await func(*args, **kwargs)

            async with db_session.begin():
                return_value = await func(*args, **kwargs)

            return return_value
        except Exception as error:
            logger.info(f"request hash: {get_db_session_context()}")
            logger.exception(error)
            raise

    return _wrapper

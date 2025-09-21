from typing import Awaitable, Callable

from fastapi import Request, Response
from fastapi import status as HTTPStatus

from .session import AsyncScopedSession, set_db_session_context


async def db_session_middleware_function(request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
    response = Response("Internal server error", status_code=HTTPStatus.HTTP_500_INTERNAL_SERVER_ERROR)

    try:
        set_db_session_context(session_id=hash(request))
        response = await call_next(request)

    finally:
        await AsyncScopedSession.remove()
        set_db_session_context(session_id=None)

    return response

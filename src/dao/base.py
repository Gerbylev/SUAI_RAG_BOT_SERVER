from db.session import get_session_or_create
from typing import TypeVar

from sqlalchemy import text
from sqlalchemy.orm import declarative_base

from utils.config import CONFIG

Base = declarative_base()

db_config = CONFIG.db

T = TypeVar("T")


async def next_id_from_sequence(sequence_name: str) -> int:
    session = await get_session_or_create()
    result = await session.execute(text(f"SELECT nextval('{sequence_name}')"))
    res = result.first()
    if res is None:
        raise Exception("Failed to get sequence value")
    return int(res[0])


def required(val: T | None, field_name: str | None = None) -> T:
    if val is not None:
        return val
    else:
        if field_name:
            raise Exception(f"Field {field_name} is required")
        else:
            raise Exception("Value is required")
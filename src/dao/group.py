from sqlalchemy import Column, Integer, String, delete, select

from dao.base import Base
from db.session import get_session_or_create


class Group(Base):
    __tablename__ = "groups"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(128), nullable=False, unique=True)

    @staticmethod
    async def get_all() -> list["Group"]:
        session = await get_session_or_create()
        result = await session.execute(select(Group))
        return list(result.scalars().all())

    @staticmethod
    async def get_by_id(group_id: int) -> "Group | None":
        session = await get_session_or_create()
        result = await session.execute(select(Group).where(Group.id == group_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def create(name: str) -> "Group":
        session = await get_session_or_create()
        group = Group(name=name)
        session.add(group)
        await session.flush()
        await session.refresh(group)
        return group

    @staticmethod
    async def delete_by_id(group_id: int) -> bool:
        session = await get_session_or_create()
        result = await session.execute(delete(Group).where(Group.id == group_id))
        await session.flush()
        return result.rowcount > 0
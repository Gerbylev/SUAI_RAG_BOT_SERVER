from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from pydantic import BaseModel

# from core.models import AgentStatesEnum
from utils.logger import get_logger

if TYPE_CHECKING:
    from core.models import ResearchContext

logger = get_logger("core.base_tool")


class BaseTool(BaseModel):
    tool_name: ClassVar[str] = None
    description: ClassVar[str] = None

    async def __call__(self, context: ResearchContext) -> str:
        raise NotImplementedError("Execute method must be implemented by subclass")

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.tool_name = cls.tool_name or cls.__name__.lower()
        cls.description = cls.description or cls.__doc__ or ""

from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import Field

from core.base_tool import BaseTool

if TYPE_CHECKING:
    from core.models import ResearchContext


class ClarificationTool(BaseTool):
    reasoning: str = Field(description="Why clarification is needed (1-2 sentences MAX)", max_length=200)
    unclear_terms: list[str] = Field(
        description="List of unclear terms (brief, 1-3 words each)",
        min_length=1,
        max_length=3,
    )
    assumptions: list[str] = Field(
        description="Possible interpretations (short, 1 sentence each)",
        min_length=2,
        max_length=3,
    )
    questions: list[str] = Field(
        description="3 specific clarifying questions (short and direct)",
        min_length=3,
        max_length=3,
    )

    async def __call__(self, context: ResearchContext) -> str:
        return "\n".join(self.questions)

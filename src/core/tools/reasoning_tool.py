from __future__ import annotations

from pydantic import Field

from core.base_tool import BaseTool


class ReasoningTool(BaseTool):
    reasoning_steps: list[str] = Field(
        description="Step-by-step reasoning (brief, 1 sentence each)",
        min_length=2,
        max_length=3,
    )

    current_situation: str = Field(
        description="Current research situation (2-3 sentences MAX)",
        max_length=300,
    )
    plan_status: str = Field(
        description="Status of current plan (1 sentence)",
        max_length=150,
    )
    enough_data: bool = Field(
        default=False,
        description="Sufficient data collected for comprehensive report?",
    )

    remaining_steps: list[str] = Field(
        description="1-3 remaining steps (brief, action-oriented)",
        min_length=1,
        max_length=3,
    )
    task_completed: bool = Field(description="Is the research task finished?")

    async def __call__(self, *args, **kwargs):
        return self.model_dump_json(
            indent=2,
        )

from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import Field

from core.base_tool import BaseTool

if TYPE_CHECKING:
    from core.models import ResearchContext


class ScheduleTool(BaseTool):
    """Tool for retrieving class schedules, including time, location, and professor information."""

    query_type: str = Field(description="Type of schedule query: 'student', 'professor', 'group', 'room', or 'subject'")
    target: str = Field(description="Name/ID of student, professor, group, room, or subject")
    date_range: str | None = Field(default=None, description="Optional date range (e.g., 'today', 'tomorrow', 'this week', '2025-10-23')")
    additional_filters: dict[str, str] | None = Field(default=None, description="Optional additional filters (e.g., {'building': 'A', 'floor': '2'})")

    async def __call__(self, context: "ResearchContext") -> str:
        # TODO: Implement actual schedule retrieval from database
        # This is a stub implementation
        result = {
            "query_type": self.query_type,
            "target": self.target,
            "date_range": self.date_range or "not specified",
            "filters": self.additional_filters or {},
            "schedule": [
                # Stub data
                {
                    "time": "09:00-10:30",
                    "subject": "Example Subject",
                    "room": "A-101",
                    "professor": "Example Professor",
                    "type": "Lecture",
                }
            ],
            "note": "This is a stub implementation. Real schedule data will be retrieved from database.",
        }
        return self.model_dump_json(indent=2) + f"\n\nStub Result: {result}"

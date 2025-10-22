from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import Field

from core.base_tool import BaseTool

if TYPE_CHECKING:
    from core.models import ResearchContext


class MapTool(BaseTool):
    """Tool for navigation and location queries within the university campus."""

    query_type: str = Field(description="Type of navigation query: 'find_room', 'route', 'building_info', 'facilities', or 'nearest'")
    location_from: str | None = Field(default=None, description="Starting point (for route queries)")
    location_to: str | None = Field(default=None, description="Destination (room number, building name, or facility)")
    facility_type: str | None = Field(default=None, description="Type of facility to find: 'cafeteria', 'library', 'restroom', 'parking', etc.")
    building: str | None = Field(default=None, description="Specific building name or code (e.g., 'A', 'B', 'Main')")

    async def __call__(self, context: "ResearchContext") -> str:
        # TODO: Implement actual map/navigation logic
        # This is a stub implementation
        result = {
            "query_type": self.query_type,
            "from": self.location_from or "current location",
            "to": self.location_to or "not specified",
            "facility_type": self.facility_type,
            "building": self.building,
            "navigation_info": {
                "distance": "50m",
                "estimated_time": "2 minutes",
                "directions": ["Go straight", "Turn right at the corridor", "Room is on the left"],
                "floor": 2,
            },
            "note": "This is a stub implementation. Real navigation data will be retrieved from map database.",
        }
        return self.model_dump_json(indent=2) + f"\n\nStub Result: {result}"

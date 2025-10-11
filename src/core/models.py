from enum import Enum

from pydantic import BaseModel, Field


class SourceData(BaseModel):
    number: int = Field(description="Citation number")
    snippet: str = Field(default="", description="Search snippet or summary")
    full_content: str = Field(default="", description="Full scraped content")
    char_count: int = Field(default=0, description="Character count of full content")

class AgentStatesEnum(str, Enum):
    INITED = "inited"
    RESEARCHING = "researching"
    WAITING_FOR_CLARIFICATION = "waiting_for_clarification"
    COMPLETED = "completed"
    ERROR = "error"
    FAILED = "failed"

    FINISH_STATES = {COMPLETED, FAILED, ERROR}
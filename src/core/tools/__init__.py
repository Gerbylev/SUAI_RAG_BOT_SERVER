from core.base_tool import BaseTool
from core.next_step_tool import (
    NextStepToolsBuilder,
    NextStepToolStub,
)
from core.tools.adapt_plan_tool import AdaptPlanTool
from core.tools.clarification_tool import ClarificationTool
from core.tools.final_answer_tool import FinalAnswerTool
from core.tools.general_info_tool import GeneralInfoTool
from core.tools.generate_plan_tool import GeneratePlanTool
from core.tools.map_tool import MapTool
from core.tools.reasoning_tool import ReasoningTool
from core.tools.schedule_tool import ScheduleTool

# Tool lists for backward compatibility
system_agent_tools = [
    ClarificationTool,
    GeneratePlanTool,
    AdaptPlanTool,
    FinalAnswerTool,
    ReasoningTool,
]

# University-specific tools
university_tools = [
    ScheduleTool,
    MapTool,
    GeneralInfoTool,
]


__all__ = [
    # Base classes
    "BaseTool",
    "NextStepToolStub",
    "NextStepToolsBuilder",
    # Individual tools
    "ClarificationTool",
    "GeneratePlanTool",
    "AdaptPlanTool",
    "FinalAnswerTool",
    "ReasoningTool",
    "ScheduleTool",
    "MapTool",
    "GeneralInfoTool",
    # Tool lists
    "NextStepToolStub",
    "NextStepToolsBuilder",
    # Tool Collections
    "system_agent_tools",
    "university_tools",
]

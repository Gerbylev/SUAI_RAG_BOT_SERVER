from typing import Literal, Type

from openai import pydantic_function_tool
from openai.types.chat import ChatCompletionFunctionToolParam

from core.agents.base_agent import BaseAgent
from core.tools import (
    BaseTool,
    ClarificationTool,
    FinalAnswerTool,
    ReasoningTool,
    system_agent_tools,
)
from core.tools.general_info_tool import GeneralInfoTool
from core.tools.map_tool import MapTool
from core.tools.schedule_tool import ScheduleTool
from utils.config import CONFIG

# University-specific tools
university_tools = [
    ScheduleTool,
    MapTool,
    GeneralInfoTool,
]


class UniversityAssistantAgent(BaseAgent):
    """University Assistant Agent for handling schedule, navigation, and general information queries.

    This agent routes user requests to appropriate tools:
    - ScheduleTool: for class schedules, professor schedules, room bookings
    - MapTool: for campus navigation and location queries
    - GeneralInfoTool: for general university information using RAG/knowledge base
    """

    name: str = "university_assistant_agent"

    def __init__(
        self,
        task: str,
        toolkit: list[Type[BaseTool]] | None = None,
        max_clarifications: int = 3,
        max_iterations: int = 10,
    ):
        super().__init__(
            task=task,
            toolkit=toolkit,
            max_clarifications=max_clarifications,
            max_iterations=max_iterations,
        )

        self.toolkit = [
            *system_agent_tools,
            *university_tools,
            *(toolkit if toolkit else []),
        ]
        self.toolkit.remove(ReasoningTool)  # LLM will do reasoning internally

        self.tool_choice: Literal["required"] = "required"

    async def _prepare_tools(self) -> list[ChatCompletionFunctionToolParam]:
        """Prepare tool classes with current context limits."""
        tools = set(self.toolkit)

        # Force completion if max iterations reached
        if self._context.iteration >= self.max_iterations:
            tools = {
                FinalAnswerTool,
            }

        # Disable clarification if limit reached
        if self._context.clarifications_used >= self.max_clarifications:
            tools -= {
                ClarificationTool,
            }

        return [pydantic_function_tool(tool, name=tool.tool_name, description=tool.description) for tool in tools]

    async def _reasoning_phase(self) -> None:
        """No explicit reasoning phase, reasoning is done internally by LLM."""
        return None

    async def _select_action_phase(self, reasoning=None) -> BaseTool:
        """Select appropriate tool based on LLM's function calling decision."""
        async with self.openai_client.chat.completions.stream(
            model=CONFIG.openai.model,
            messages=await self._prepare_context(),
            max_tokens=CONFIG.openai.max_tokens,
            temperature=CONFIG.openai.temperature,
            tools=await self._prepare_tools(),
            tool_choice=self.tool_choice,
        ) as stream:
            async for event in stream:
                if event.type == "chunk":
                    self.streaming_generator.add_chunk(event)

        tool = (await stream.get_final_completion()).choices[0].message.tool_calls[0].function.parsed_arguments

        if not isinstance(tool, BaseTool):
            raise ValueError("Selected tool is not a valid BaseTool instance")

        self.conversation.append(
            {
                "role": "assistant",
                "content": None,
                "tool_calls": [
                    {
                        "type": "function",
                        "id": f"{self._context.iteration}-action",
                        "function": {
                            "name": tool.tool_name,
                            "arguments": tool.model_dump_json(),
                        },
                    }
                ],
            }
        )
        self.streaming_generator.add_tool_call(f"{self._context.iteration}-action", tool.tool_name, tool.model_dump_json())
        return tool

    async def _action_phase(self, tool: BaseTool) -> str:
        """Execute the selected tool and update conversation context."""
        result = await tool(self._context)
        self.conversation.append({"role": "tool", "content": result, "tool_call_id": f"{self._context.iteration}-action"})
        self.streaming_generator.add_chunk_from_str(f"{result}\n")
        self._log_tool_execution(tool, result)
        return result


if __name__ == "__main__":
    import asyncio

    async def main():
        # Example usage
        agent = UniversityAssistantAgent(
            task="Когда у группы ИВТ-21 следующая пара по математике?",
            max_iterations=5,
            max_clarifications=2,
        )
        await agent.execute()

    asyncio.run(main())

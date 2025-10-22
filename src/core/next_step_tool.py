import operator
from abc import ABC
from functools import reduce
from typing import Annotated, Literal, Type, TypeVar

from pydantic import BaseModel, Field, create_model

from core.base_tool import BaseTool
from core.tools.reasoning_tool import ReasoningTool
from utils.logger import get_logger

logger = get_logger("core.next_step_tool")

T = TypeVar("T", bound=BaseTool)


class NextStepToolStub(ReasoningTool, ABC):
    function: T = Field(description="Select the appropriate tool for the next step")


class DiscriminantToolMixin(BaseModel):
    tool_name_discriminator: str = Field(..., description="Tool name discriminator")

    def model_dump(self, *args, **kwargs):
        exclude = kwargs.pop("exclude", set())
        exclude = exclude.union({"tool_name_discriminator"})
        return super().model_dump(*args, exclude=exclude, **kwargs)


class NextStepToolsBuilder:
    @classmethod
    def _create_discriminant_tool(cls, tool_class: Type[T]) -> Type[BaseModel]:
        return create_model(  # noqa
            f"D_{tool_class.__name__}",
            __base__=(tool_class, DiscriminantToolMixin),  # the order matters here
            tool_name_discriminator=(Literal[tool_class.tool_name], Field(..., description="Tool name discriminator")),
        )

    @classmethod
    def _create_tool_types_union(cls, tools_list: list[Type[T]]) -> Type:
        if len(tools_list) == 1:
            return cls._create_discriminant_tool(tools_list[0])
        discriminant_tools = [cls._create_discriminant_tool(tool) for tool in tools_list]
        union = reduce(operator.or_, discriminant_tools)
        return Annotated[union, Field()]

    @classmethod
    def build_NextStepTools(cls, tools_list: list[Type[T]]) -> Type[NextStepToolStub]:  # noqa
        return create_model(
            "NextStepTools",
            __base__=NextStepToolStub,
            function=(cls._create_tool_types_union(tools_list), Field()),
        )

from typing import Annotated, Literal, TypedDict

from langchain_core.messages import AIMessage, AnyMessage, BaseMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, add_messages
from langgraph.graph.state import CompiledStateGraph
from langgraph.prebuilt import ToolNode
from pydantic import SecretStr

from agent.tools import get_department_schedule, get_group_schedule, get_room_schedule, get_teacher_schedule
from utils.config import CONFIG
from utils.logger import get_logger

logger = get_logger("AgentGraph")


class AgentState(TypedDict):
    """Состояние агента"""

    messages: Annotated[list[AnyMessage], add_messages]
    group_number: int | None


def create_llm_with_tools():
    """Создает LLM с подключенными инструментами"""
    llm = ChatOpenAI(
        model=CONFIG.gpt.model,
        api_key=SecretStr(CONFIG.gpt.api_key),
        base_url=CONFIG.gpt.base_url,
        temperature=0,
    )

    tools = [get_teacher_schedule, get_group_schedule, get_department_schedule, get_room_schedule]
    return llm.bind_tools(tools)


async def agent_node(state: AgentState) -> dict[str, list[BaseMessage]]:
    """Узел с агентом на основе LLM"""
    messages = state["messages"]
    group_number = state.get("group_number")

    # Создаем LLM с инструментами
    llm_with_tools = create_llm_with_tools()

    # Добавляем системное сообщение с контекстом
    system_message = """Ты - помощник для студентов ГУАП.
Твоя задача - помогать с информацией о расписании.

Доступные функции:
- get_teacher_schedule: получение расписания преподавателя по имени
- get_group_schedule: получение расписания группы по номеру
- get_department_schedule: получение расписания кафедры по названию
- get_room_schedule: получение расписания аудитории по номеру

Когда пользователь спрашивает про расписание, определи что именно его интересует
(преподаватель, группа, кафедра или аудитория) и используй соответствующую функцию.
Поисковые запросы могут быть не полными - функции найдут наиболее подходящие варианты.

Отвечай на русском языке, будь вежливым и полезным."""

    if group_number:
        system_message += f"\n\nПользователь из группы {group_number}."

    # Формируем сообщения для LLM
    from langchain_core.messages import SystemMessage

    llm_messages = [SystemMessage(content=system_message)] + messages

    # Вызываем LLM
    response = await llm_with_tools.ainvoke(llm_messages)

    return {"messages": [response]}


def should_continue(state: AgentState) -> Literal["tools", "__end__"]:
    """Определяет, нужно ли вызывать инструменты или завершить работу"""
    messages = state["messages"]
    last_message = messages[-1] if messages else None

    # Если последнее сообщение содержит вызов инструмента - идем к инструментам
    if last_message and isinstance(last_message, AIMessage) and hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"

    return "__end__"


def create_agent_graph() -> CompiledStateGraph:
    """Создаёт и компилирует граф агента"""
    workflow = StateGraph(AgentState)

    # Создаем узел с инструментами
    tool_node = ToolNode([get_teacher_schedule, get_group_schedule, get_department_schedule, get_room_schedule])

    # Добавляем узлы
    workflow.add_node("agent", agent_node)
    workflow.add_node("tools", tool_node)

    # Устанавливаем точку входа
    workflow.set_entry_point("agent")

    # Добавляем условные переходы
    workflow.add_conditional_edges("agent", should_continue, {"tools": "tools", "__end__": "__end__"})

    # После вызова инструмента возвращаемся к агенту
    workflow.add_edge("tools", "agent")

    return workflow.compile()
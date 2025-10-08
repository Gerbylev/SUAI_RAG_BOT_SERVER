from langchain_core.messages import HumanMessage

from agent.graph import create_agent_graph


class AgentService:
    """Сервис для управления агентом"""

    def __init__(self):
        self.graph = create_agent_graph()
        self.sessions: dict[str, dict] = {}

    async def process_message(self, user_id: str, message: str) -> str:
        """Обрабатывает сообщение пользователя"""
        if user_id not in self.sessions:
            self.sessions[user_id] = {"messages": [], "group_number": None}

        session = self.sessions[user_id]

        result = await self.graph.ainvoke(
            {"messages": session["messages"] + [HumanMessage(content=message)], "group_number": session["group_number"]}
        )

        self.sessions[user_id] = result

        messages = result.get("messages", [])
        if messages:
            last_message = messages[-1]
            return last_message.content if hasattr(last_message, "content") else str(last_message)

        return "Нет ответа"

    async def get_group_number(self, user_id: str) -> int | None:
        """Получает номер группы пользователя"""
        if user_id in self.sessions:
            return self.sessions[user_id].get("group_number")
        return None

    async def get_history(self, user_id: str) -> list[dict]:
        """Получает историю сообщений пользователя"""
        if user_id in self.sessions:
            messages = self.sessions[user_id].get("messages", [])
            return [
                {
                    "role": msg.get("role") if isinstance(msg, dict) else getattr(msg, "role", "unknown"),
                    "content": msg.get("content") if isinstance(msg, dict) else getattr(msg, "content", "")
                }
                for msg in messages
            ]
        return []


# Глобальный экземпляр сервиса
agent_service = AgentService()
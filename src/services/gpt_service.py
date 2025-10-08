from typing import List, Dict, Optional

from openai import AsyncOpenAI

from utils.config import CONFIG
from utils.logger import get_logger

logger = get_logger("GPTService")


class GPTService:

    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=CONFIG.gpt.api_key,
            base_url=CONFIG.gpt.base_url,
        )
        self.model = CONFIG.gpt.model

    async def send_message(self, messages: List[Dict[str, str]]) -> str:
        logger.info(f"Отправка запроса в GPT: {len(messages)} сообщений")

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,  # type: ignore
            )

            answer = response.choices[0].message.content or ""

            logger.info(f"Получен ответ от GPT: {len(answer)} символов")
            return answer

        except Exception as e:
            logger.error(f"Ошибка при запросе к GPT: {e}")
            raise

    async def chat(self, user_message: str, context: Optional[str] = None) -> str:
        """
        Упрощенный метод для отправки одного сообщения от пользователя

        Args:
            user_message: Текст сообщения пользователя
            context: Дополнительный контекст из базы знаний (опционально)

        Returns:
            str: Ответ от GPT
        """
        if context:
            # Формируем системное сообщение с контекстом
            messages = [
                {
                    "role": "system",
                    "content": f"Используй следующий контекст для ответа на вопрос пользователя:\n\n{context}",
                },
                {"role": "user", "content": user_message},
            ]
        else:
            messages = [{"role": "user", "content": user_message}]

        return await self.send_message(messages)

    async def chat_with_rag(
        self, user_message: str, collection_name: str, top_k: int = 3
    ) -> str:
        """
        Отправляет сообщение в GPT с контекстом из Qdrant

        Args:
            user_message: Текст сообщения пользователя
            collection_name: Название коллекции в Qdrant
            top_k: Количество документов для контекста

        Returns:
            str: Ответ от GPT
        """
        from services.qdrant_service import qdrant_service

        try:
            # Ищем релевантные документы
            documents = await qdrant_service.search(
                collection_name=collection_name, query=user_message, limit=top_k
            )

            # Формируем контекст из найденных документов
            if documents:
                context = "\n\n".join([doc["text"] for doc in documents])
                logger.info(f"Найдено {len(documents)} релевантных документов для контекста")
            else:
                context = None
                logger.warning("Релевантные документы не найдены")

            return await self.chat(user_message, context=context)

        except Exception as e:
            logger.error(f"Ошибка при работе с RAG: {e}")
            # Если ошибка - отвечаем без контекста
            return await self.chat(user_message)


gpt_service = GPTService()
from typing import List, Dict

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

    async def chat(self, user_message: str) -> str:
        messages = [{"role": "user", "content": user_message}]
        return await self.send_message(messages)


gpt_service = GPTService()
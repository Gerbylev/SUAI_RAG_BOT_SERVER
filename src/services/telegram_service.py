import asyncio
from typing import Awaitable, Callable

from aiogram import Bot, Dispatcher
from aiogram.types import Message, Update
from aiogram.enums import ChatAction

from utils.config import CONFIG
from utils.logger import get_logger
from services.gpt_service import gpt_service

log = get_logger("TelegramService")


class TelegramService:
    def __init__(self):
        self.bot: Bot | None = None
        self.dispatcher: Dispatcher | None = None
        self.polling_task: asyncio.Task | None = None
        self.message_handler: Callable[[Message], None | Awaitable[None]] | None = None

    async def start(self):
        if not CONFIG.telegram.enabled:
            log.info("Telegram bot is disabled in configuration")
            return

        if not CONFIG.telegram.bot_token:
            log.warning("Telegram bot token is not configured")
            return

        log.info(f"Starting Telegram bot in {CONFIG.telegram.mode} mode...")
        self.bot = Bot(token=CONFIG.telegram.bot_token)
        self.dispatcher = Dispatcher()

        @self.dispatcher.message()
        async def handle_message(message: Message):
            log.info(f"Received message from {message.from_user.id}: {message.text}")

            if message.text:
                try:
                    await self.bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.TYPING)

                    response = await gpt_service.chat(message.text)

                    await message.answer(response)

                except Exception as e:
                    log.error(f"Error processing message: {e}", exc_info=True)
                    await message.answer("Извините, произошла ошибка при обработке вашего сообщения.")

            if self.message_handler:
                await self.message_handler(message)

        if CONFIG.telegram.mode == "polling":
            self.polling_task = asyncio.create_task(self._run_polling())
            log.info("Telegram bot started in polling mode")
        elif CONFIG.telegram.mode == "webhook":
            log.info("Telegram bot started in webhook mode")
            raise NotImplemented # TODO Implement
        else:
            log.error(f"Unknown Telegram mode: {CONFIG.telegram.mode}")

    async def _run_polling(self):
        try:
            log.info("Starting Telegram polling...")
            await self.dispatcher.start_polling(self.bot, handle_signals=False)
        except asyncio.CancelledError:
            log.info("Telegram polling cancelled")
        except Exception as e:
            log.error(f"Error in Telegram polling: {e}", exc_info=True)


    async def stop(self):
        log.info("Stopping Telegram bot...")

        if CONFIG.telegram.mode == "polling" and self.polling_task:
            self.polling_task.cancel()
            try:
                await self.polling_task
            except asyncio.CancelledError:
                pass
        elif CONFIG.telegram.mode == "webhook" and self.bot:
            try:
                await self.bot.delete_webhook(drop_pending_updates=True)
                log.info("Webhook deleted")
            except Exception as e:
                log.error(f"Error deleting webhook: {e}")

        if self.bot:
            await self.bot.session.close()

        log.info("Telegram bot stopped")

    def set_message_handler(self, handler: Callable[[Message], None]):
        self.message_handler = handler

    async def send_message(self, chat_id: int, text: str):
        if self.bot:
            await self.bot.send_message(chat_id=chat_id, text=text)

    async def process_update(self, update: Update):
        if self.dispatcher:
            await self.dispatcher.feed_update(self.bot, update)


telegram_service = TelegramService()
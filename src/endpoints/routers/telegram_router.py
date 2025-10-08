from aiogram.types import Update
from fastapi import APIRouter, Request

from services.telegram_service import telegram_service
from utils.config import CONFIG
from utils.logger import get_logger

log = get_logger("TelegramRouter")

telegram_routes = APIRouter()


@telegram_routes.post(f"/{CONFIG.telegram.bot_token}")
async def telegram_webhook(request: Request):
    if not CONFIG.telegram.enabled:
        log.warning("Received webhook request but Telegram is disabled")
        return {"status": "disabled"}

    if CONFIG.telegram.mode != "webhook":
        log.warning(f"Received webhook request but bot is in {CONFIG.telegram.mode} mode")
        return {"status": "wrong_mode"}

    try:
        update_data = await request.json()
        log.debug(f"Received webhook update: {update_data}")

        update = Update(**update_data)

        await telegram_service.process_update(update)

        return {"status": "ok"}

    except Exception as e:
        log.error(f"Error processing webhook: {e}", exc_info=True)
        return {"status": "error", "message": str(e)}
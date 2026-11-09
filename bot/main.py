"""Minimal Telegram bot runtime for the informational ИНЕЙ mini app."""
import asyncio
import logging
import os
from urllib.parse import urlparse

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("iney.bot")

async def start(message: Message) -> None:
    url = os.environ.get("MINI_APP_URL", "").strip()
    if not url:
        await message.answer("Приложение временно недоступно.")
        return
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="Открыть информационный каталог", web_app=WebAppInfo(url=url))
    ]])
    await message.answer(
        "ИНЕЙ — информационный каталог. 18+. Никотин вызывает зависимость. "
        "Продажа несовершеннолетним запрещена.",
        reply_markup=keyboard,
    )

async def main() -> None:
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    url = os.environ.get("MINI_APP_URL", "").strip()
    parsed = urlparse(url)
    if not token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is missing")
    if parsed.scheme != "https" or not parsed.netloc or parsed.username or parsed.password:
        raise RuntimeError("MINI_APP_URL must be a public HTTPS URL")
    bot = Bot(token=token)
    dp = Dispatcher()
    dp.message.register(start, CommandStart())
    try:
        # Polling requires one active instance and no webhook.
        await bot.delete_webhook(drop_pending_updates=False)
        me = await bot.get_me()
        log.info("Starting bot @%s", me.username)
        await dp.start_polling(bot, allowed_updates=["message"])
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())

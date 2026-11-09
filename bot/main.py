"""Telegram informational Mini App bot with single-message chat UI."""
import asyncio
import logging
import os
from urllib.parse import urlparse

from aiogram import Bot, Dispatcher
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError
from aiogram.filters import CommandStart
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("iney.bot")

# Tracks only messages sent by this bot; does not delete users' messages.
# Volatile by design: old replies cannot be cleaned after a worker restart.
last_reply: dict[int, int] = {}
chat_locks: dict[int, asyncio.Lock] = {}


async def replace_reply(message: Message, text: str, reply_markup=None) -> None:
    chat_id = message.chat.id
    lock = chat_locks.setdefault(chat_id, asyncio.Lock())
    async with lock:
        previous = last_reply.get(chat_id)
        if previous is not None:
            try:
                await message.bot.delete_message(chat_id=chat_id, message_id=previous)
            except (TelegramBadRequest, TelegramForbiddenError) as exc:
                log.info("Cannot delete previous bot message in chat %s: %s", chat_id, exc)
        sent = await message.answer(text, reply_markup=reply_markup)
        last_reply[chat_id] = sent.message_id


async def start(message: Message) -> None:
    url = os.environ.get("MINI_APP_URL", "").strip()
    if not url:
        await replace_reply(message, "Приложение временно недоступно.")
        return
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="Открыть информационный каталог", web_app=WebAppInfo(url=url))
    ]])
    await replace_reply(
        message,
        "ИНЕЙ — информационный каталог. 18+. Никотин вызывает зависимость. "
        "Продажа несовершеннолетним запрещена.",
        reply_markup=keyboard,
    )


async def help_message(message: Message) -> None:
    await replace_reply(
        message,
        "Для открытия информационного каталога отправьте /start. "
        "По вопросам безопасности и эксплуатации устройства опишите ваш вопрос.",
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
    dp.message.register(help_message)
    try:
        await bot.delete_webhook(drop_pending_updates=False)
        me = await bot.get_me()
        log.info("Starting bot @%s", me.username)
        await dp.start_polling(bot, allowed_updates=["message"])
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())

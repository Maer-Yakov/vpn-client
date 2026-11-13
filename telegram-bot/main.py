from __future__ import annotations

import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand

from config import load_settings
from db import Database
from handlers import admin, chat, image, start, subscription
from middlewares.private import PrivateChatMiddleware
from middlewares.user import UserMiddleware

logger = logging.getLogger(__name__)


async def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
    settings = load_settings()
    database = Database(settings.db_path)
    await database.connect()
    bot = Bot(token=settings.bot_token)
    dispatcher = Dispatcher(storage=MemoryStorage())
    dispatcher.message.middleware(PrivateChatMiddleware())
    dispatcher.callback_query.middleware(PrivateChatMiddleware())
    dispatcher.message.middleware(UserMiddleware())
    dispatcher.callback_query.middleware(UserMiddleware())

    dispatcher.include_router(start.router)
    dispatcher.include_router(subscription.router)
    dispatcher.include_router(admin.router)
    dispatcher.include_router(chat.router)
    dispatcher.include_router(image.router)
    dispatcher.include_router(start.fallback_router)

    await bot.set_my_commands(
        [
            BotCommand(command="start", description="Главное меню"),
            BotCommand(command="profile", description="Мой профиль"),
        ]
    )
    logger.info("long polling started, db=%s", settings.db_path)
    try:
        await dispatcher.start_polling(bot, settings=settings, db=database)
    finally:
        await database.close()
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())

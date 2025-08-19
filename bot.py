import asyncio
import urllib
import os
import time

from aiogram import Bot, Dispatcher
from aiogram.client.bot import DefaultBotProperties
from aiogram.fsm.storage.redis import DefaultKeyBuilder, RedisStorage
from aiogram.utils.callback_answer import CallbackAnswerMiddleware
from aiogram_dialog import setup_dialogs
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from config_data import config
from database.base import Base
from dialogs import admin_dialog, registration_dialog, schedule_dialog
from handlers import commands_router, messages_router
from keyboards.commands_menu import set_main_menu
from middlewares import (
    DbSessionMiddleware,
    GetLangMiddleware,
    MessageThrottlingMiddleware,
)
from services import (
    populate_initial_faculties,
    populate_initial_lastday,
    populate_initial_timetable,
    setup_logger,
    send_notifications,
)

os.environ["TZ"] = "Europe/Moscow"
time.tzset()


async def main() -> None:
    """Initializes and starts the bot."""
    setup_logger("INFO")

    # --- Initializing Bot and Storages ---
    bot = Bot(token=config.bot.token, default=DefaultBotProperties(parse_mode="HTML"))

    bot_storage = RedisStorage.from_url(
        f"redis://{config.redis.user}:{urllib.parse.quote_plus(config.redis.password)}@{config.redis.host}:{config.redis.port}/{config.redis.bot_database}",
        key_builder=DefaultKeyBuilder(with_destiny=True),
    )
    middleware_storage = RedisStorage.from_url(
        f"redis://{config.redis.user}:{urllib.parse.quote_plus(config.redis.password)}@{config.redis.host}:{config.redis.port}/{config.redis.middleware_database}",
    )

    dp = Dispatcher(storage=bot_storage)

    # --- Database Initialization ---
    engine = create_async_engine(url=config.db.url, echo=False)
    session_maker = async_sessionmaker(engine, expire_on_commit=False)

    # --- Create tables and populate initial data ---
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    await populate_initial_faculties(session_maker)
    await populate_initial_timetable(session_maker)
    await populate_initial_lastday(session_maker)

    # --- Middlewares Setup ---
    dp.update.middleware(DbSessionMiddleware(session_pool=session_maker))
    dp.update.middleware(GetLangMiddleware())
    dp.message.middleware(MessageThrottlingMiddleware(storage=middleware_storage))
    dp.callback_query.middleware(CallbackAnswerMiddleware())

    # --- Routers and Dialogs Setup ---
    dp.include_router(commands_router)
    dp.include_router(registration_dialog)
    dp.include_router(schedule_dialog)
    dp.include_router(admin_dialog)
    dp.include_router(messages_router)  # Must be last for other messages

    setup_dialogs(dp)

    # --- Scheduler Setup ---
    scheduler = AsyncIOScheduler(timezone="Europe/Moscow")
    scheduler.add_job(
        send_notifications,
        "cron",
        hour="8-18",
        minute="*/5",
        args=[bot, session_maker],
    )
    scheduler.start()

    # --- Bot Startup ---
    await set_main_menu(bot)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

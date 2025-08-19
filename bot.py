import asyncio
import urllib

from aiogram import Bot, Dispatcher
from aiogram.client.bot import DefaultBotProperties
from aiogram.fsm.storage.redis import DefaultKeyBuilder, RedisStorage
from aiogram.utils.callback_answer import CallbackAnswerMiddleware
from aiogram_dialog import setup_dialogs
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from config_data import config
from database.base import Base
from keyboards.commands_menu import set_main_menu
from middlewares import DbSessionMiddleware, GetLangMiddleware
from services import setup_logger

# TODO: Import routers and dialogs later
# from handlers import commands_router
# from dialogs import registration_dialog


async def main() -> None:
    """Initializes and starts the bot."""
    setup_logger("INFO")

    # --- Initializing Bot and Storages ---
    bot = Bot(token=config.bot.token, default=DefaultBotProperties(parse_mode="HTML"))

    bot_storage = RedisStorage.from_url(
        f"redis://{config.redis.user}:{urllib.parse.quote_plus(config.redis.password)}@{config.redis.host}:{config.redis.port}/{config.redis.bot_database}",
        key_builder=DefaultKeyBuilder(with_destiny=True),
    )
    # Note: for throttling or other middleware, a separate storage can be used.
    # middleware_storage = RedisStorage.from_url(...)

    dp = Dispatcher(storage=bot_storage)

    # --- Database Initialization ---
    engine = create_async_engine(url=config.db.url, echo=False)
    async with engine.begin() as conn:
        # This will create tables if they don't exist. For changes, use Alembic.
        await conn.run_sync(Base.metadata.create_all)
    session_maker = async_sessionmaker(engine, expire_on_commit=False)

    # --- Middlewares Setup ---
    dp.update.middleware(DbSessionMiddleware(session_pool=session_maker))
    dp.update.middleware(GetLangMiddleware())
    dp.callback_query.middleware(CallbackAnswerMiddleware())

    # --- Routers and Dialogs Setup ---
    # TODO: Include routers and dialogs here
    # dp.include_router(registration_dialog)
    # dp.include_router(commands_router)

    # Must be the last one to register handlers
    setup_dialogs(dp)

    # --- Bot Startup ---
    await set_main_menu(bot)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

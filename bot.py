import asyncio
import urllib
from zoneinfo import ZoneInfo

from aiogram import Bot, Dispatcher
from aiogram.client.bot import DefaultBotProperties
from aiogram.fsm.storage.redis import DefaultKeyBuilder, RedisStorage
from aiogram.utils.callback_answer import CallbackAnswerMiddleware
from aiogram.webhook.aiohttp_server import SimpleRequestHandler
from aiogram_dialog import setup_dialogs
from aiohttp import web
from loguru import logger
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy import text

from config_data import config
from database.base import Base
from dialogs import (
    admin_dialog,
    booking_management_dialog,
    registration_dialog,
    schedule_dialog,
)
from handlers import commands_router, messages_router
from keyboards import set_main_menu
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
)

__version__ = "2.0.0"


async def on_startup(bot: Bot, session_maker: async_sessionmaker) -> None:
    """A function that is executed when the bot starts."""
    # --- Create tables and populate initial data ---
    engine = session_maker.kw["bind"]
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    await populate_initial_faculties(session_maker)
    await populate_initial_timetable(session_maker)
    await populate_initial_lastday(session_maker)

    # --- Set webhook if URL is provided ---
    if config.webhook.base_url:
        webhook_url = f"{config.webhook.base_url}{config.webhook.path}"
        await bot.set_webhook(url=webhook_url)
        logger.info(f"Webhook set to {webhook_url}")
    else:
        logger.info("Webhook not set, running in polling mode.")

    # --- Set main menu commands ---
    await set_main_menu(bot)


async def on_shutdown(bot: Bot) -> None:
    """A function that is executed when the bot is shut down."""
    logger.info("Bot is shutting down...")
    await bot.delete_webhook(drop_pending_updates=True)
    logger.info("Webhook deleted.")


async def main() -> None:
    """Initializes and starts the bot."""
    setup_logger("INFO")

    logger.info(f"Starting DAS Payment Bot version {__version__}")

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
    engine = create_async_engine(
        url=config.db.url,
        echo=False,
        pool_pre_ping=True,  # Check connection before use
    )
    session_maker = async_sessionmaker(engine, expire_on_commit=False)

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
    dp.include_router(booking_management_dialog)
    dp.include_router(messages_router)  # Must be last for other messages

    setup_dialogs(dp)

    # --- Bot Startup ---
    await on_startup(bot, session_maker)
    dp.shutdown.register(on_shutdown)

    if config.webhook.base_url:
        # --- Webhook Mode ---
        logger.info("Starting bot in webhook mode...")

        # --- Health check handlers for Kubernetes ---
        async def liveness_probe(request):
            """Liveness probe endpoint."""
            try:
                logger.debug("Liveness probe successful.")
                return web.Response(text="OK", status=200)
            except Exception as e:
                logger.error(f"Liveness probe failed: {e.__class__.__name__} - {e}")
                return web.Response(
                    text=f"Service Unavailable: {e.__class__.__name__}", status=503
                )
        

        async def readiness_probe(request):
            """
            Readiness probe endpoint that checks connections to all critical services.
            """
            try:
                # 1. Check Telegram API connection
                await bot.get_me()

                # 2. Check Database connection by executing a simple query
                async with session_maker() as session:
                    await session.execute(text("SELECT 1"))

                # 3. Check Redis connection
                await bot_storage.redis.ping()

                logger.debug("Readiness probe successful.")
                return web.Response(text="OK", status=200)
            except Exception as e:
                logger.error(f"Readiness probe failed: {e.__class__.__name__} - {e}")
                return web.Response(
                    text=f"Service Unavailable: {e.__class__.__name__}", status=503
                )

        app = web.Application()
        app.router.add_get("/health/live", liveness_probe)
        app.router.add_get("/health/ready", readiness_probe)

        webhook_requests_handler = SimpleRequestHandler(
            dispatcher=dp,
            bot=bot,
        )
        webhook_requests_handler.register(app, path=config.webhook.path)

        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, host=config.webhook.host, port=config.webhook.port)
        await site.start()

        # Keep the server running
        await asyncio.Event().wait()

    else:
        # --- Polling Mode ---
        logger.info("Starting bot in polling mode...")
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped manually.")

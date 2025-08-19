import asyncio
import urllib
from zoneinfo import ZoneInfo

from aiogram import Bot
from aiogram.client.bot import DefaultBotProperties
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from loguru import logger
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from config_data import config
from services import send_notifications, setup_logger


async def main() -> None:
    """Initializes and starts the notification scheduler service."""
    setup_logger("INFO")
    logger.info("Starting scheduler service...")

    bot = Bot(token=config.bot.token, default=DefaultBotProperties(parse_mode="HTML"))

    # --- Database Initialization ---
    engine = create_async_engine(
        url=config.db.url,
        echo=False,
        pool_pre_ping=True,
    )
    session_maker = async_sessionmaker(engine, expire_on_commit=False)

    # --- Scheduler Setup ---
    scheduler = AsyncIOScheduler(timezone=ZoneInfo("Europe/Moscow"))
    scheduler.add_job(
        send_notifications,
        "cron",
        # hour="8-18",
        # minute="*/5",
        minute="*",
        args=[bot, session_maker],
    )
    scheduler.start()
    logger.info("Scheduler configured and started.")

    # Keep the script running indefinitely
    await asyncio.Event().wait()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Scheduler service stopped.")

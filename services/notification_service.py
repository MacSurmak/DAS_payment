import datetime
from zoneinfo import ZoneInfo

from aiogram import Bot
from aiogram.types import FSInputFile
from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.orm import selectinload

from database.models import Booking
from lexicon import lexicon


async def send_notifications(bot: Bot, session_maker: async_sessionmaker[AsyncSession]):
    """
    Sends booking reminders to users.
    Checks for bookings one day and one hour in advance.
    """
    moscow_tz = ZoneInfo("Europe/Moscow")
    now_moscow = datetime.datetime.now(moscow_tz)
    logger.debug(f"Running notification job at {now_moscow.isoformat()}")

    # Convert current time to UTC to query the database correctly
    now_utc = now_moscow.astimezone(ZoneInfo("UTC"))

    # Define time windows in UTC for correct DB querying
    day_ahead_utc = now_utc + datetime.timedelta(days=1)
    hour_ahead_utc = now_utc + datetime.timedelta(hours=1)

    notification_photo = FSInputFile("assets/map.jpg")

    async with session_maker() as session:
        # Find bookings for one day ahead
        stmt_day = (
            select(Booking)
            .where(
                Booking.booking_datetime
                >= day_ahead_utc.replace(second=0, microsecond=0),
                Booking.booking_datetime
                < (day_ahead_utc + datetime.timedelta(minutes=5)).replace(
                    second=0, microsecond=0
                ),
            )
            .options(selectinload(Booking.user))
        )
        bookings_day_ahead = (await session.scalars(stmt_day)).all()

        for booking in bookings_day_ahead:
            user = booking.user
            # booking.booking_datetime is now already in Moscow time due to AwareDateTime type
            try:
                caption_text = lexicon(
                    user.lang,
                    "notification_day_before",
                    time=booking.booking_datetime.strftime("%H:%M"),
                    window=booking.window_number,
                )
                await bot.send_photo(
                    chat_id=user.telegram_id,
                    photo=notification_photo,
                    caption=caption_text,
                )
                logger.info(f"Sent 1-day reminder to user {user.telegram_id}")
            except Exception as e:
                logger.error(
                    f"Failed to send 1-day reminder to {user.telegram_id}: {e}"
                )

        # Find bookings for one hour ahead
        stmt_hour = (
            select(Booking)
            .where(
                Booking.booking_datetime
                >= hour_ahead_utc.replace(second=0, microsecond=0),
                Booking.booking_datetime
                < (hour_ahead_utc + datetime.timedelta(minutes=5)).replace(
                    second=0, microsecond=0
                ),
            )
            .options(selectinload(Booking.user))
        )
        bookings_hour_ahead = (await session.scalars(stmt_hour)).all()

        for booking in bookings_hour_ahead:
            user = booking.user
            # booking.booking_datetime is now already in Moscow time
            try:
                await bot.send_message(
                    chat_id=user.telegram_id,
                    text=lexicon(
                        user.lang,
                        "notification_hour_before",
                        time=booking.booking_datetime.strftime("%H:%M"),
                        window=booking.window_number,
                    ),
                )
                logger.info(f"Sent 1-hour reminder to user {user.telegram_id}")
            except Exception as e:
                logger.error(
                    f"Failed to send 1-hour reminder to {user.telegram_id}: {e}"
                )

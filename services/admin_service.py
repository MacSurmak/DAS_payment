import datetime
from typing import List

from aiogram import Bot
from aiogram.exceptions import TelegramAPIError
from loguru import logger
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import ScheduleException, User


async def get_statistics(session: AsyncSession) -> dict[str, int]:
    """
    Calculates statistics about bot usage.

    Args:
        session: The database session.

    Returns:
        A dictionary with statistics.
    """
    booked_users_stmt = select(func.count(User.user_id)).where(
        User.is_signed_up == True
    )
    total_users_stmt = select(func.count(User.user_id))

    booked_users = (await session.execute(booked_users_stmt)).scalar_one()
    total_users = (await session.execute(total_users_stmt)).scalar_one()

    return {"booked_users": booked_users, "total_users": total_users}


async def broadcast_message(
    bot: Bot, session: AsyncSession, text: str
) -> tuple[int, int]:
    """
    Sends a message to all registered users.

    Args:
        bot: The aiogram Bot instance.
        session: The database session.
        text: The message text to send.

    Returns:
        A tuple of (sent_count, failed_count).
    """
    users_stmt = select(User.telegram_id)
    users_result = await session.scalars(users_stmt)
    user_ids = users_result.all()

    sent_count = 0
    failed_count = 0

    logger.info(f"Starting broadcast to {len(user_ids)} users.")

    for user_id in user_ids:
        try:
            await bot.send_message(chat_id=user_id, text=text)
            sent_count += 1
        except TelegramAPIError as e:
            logger.warning(f"Failed to send broadcast message to {user_id}: {e}")
            failed_count += 1

    return sent_count, failed_count


async def block_day_in_schedule(
    session: AsyncSession, target_date: datetime.date, windows: List[int]
):
    """
    Creates ScheduleException records to make a day non-working.

    Args:
        session: The database session.
        target_date: The date to block.
        windows: A list of window numbers to block.
    """
    exceptions = []
    for window_num in windows:
        exception = ScheduleException(
            exception_date=target_date,
            start_time=datetime.time(0, 0),
            end_time=datetime.time(23, 59),
            window_number=window_num,
            is_working=False,
        )
        exceptions.append(exception)

    session.add_all(exceptions)
    await session.commit()

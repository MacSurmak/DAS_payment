import datetime
from typing import Any, Dict

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


async def create_non_working_day(
    session: AsyncSession,
    date: datetime.date,
    description: str,
):
    """
    Creates a high-priority exception to make a specific date non-working.

    Args:
        session: The database session.
        date: The date to make non-working.
        description: A description for the exception.
    """
    exception = ScheduleException(
        description=description,
        start_date=date,
        end_date=date,
        is_non_working=True,
        priority=100,  # High priority to override any other rules
        is_active=True,
    )
    session.add(exception)
    await session.commit()


async def create_schedule_exception(
    session: AsyncSession, data: Dict[str, Any]
) -> ScheduleException:
    """
    Creates a new schedule exception rule from dialog data.

    Args:
        session: The database session.
        data: The data collected from the dialog manager.

    Returns:
        The created ScheduleException object.
    """
    new_exception = ScheduleException(
        description=data.get("description"),
        start_date=datetime.date.fromisoformat(data.get("start_date")),
        end_date=datetime.date.fromisoformat(data.get("end_date")),
        target_days_of_week=[int(d) for d in data.get("days_of_week", [])] or None,
        target_start_time=(
            datetime.time.fromisoformat(data["target_slot"])
            if data.get("target_slot")
            else None
        ),
        new_start_time=(
            datetime.time.fromisoformat(data["new_start_time"])
            if data.get("new_start_time")
            else None
        ),
        new_end_time=(
            datetime.time.fromisoformat(data["new_end_time"])
            if data.get("new_end_time")
            else None
        ),
        allowed_years=data.get("years") or None,
        start_window_override=data.get("start_window"),
        is_active=True,
        priority=10,  # Default priority for custom rules
    )
    session.add(new_exception)
    await session.commit()
    return new_exception


async def delete_schedule_exception(session: AsyncSession, exception_id: int) -> bool:
    """
    Deletes a schedule exception by its ID.

    Args:
        session: The database session.
        exception_id: The ID of the exception to delete.

    Returns:
        True if deletion was successful, False otherwise.
    """
    exception = await session.get(ScheduleException, exception_id)
    if exception:
        await session.delete(exception)
        await session.commit()
        return True
    return False

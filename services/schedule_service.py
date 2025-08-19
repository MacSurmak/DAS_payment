import datetime
from typing import List, Tuple

from loguru import logger
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database.models import Booking, Faculty, TimetableSlot, User


async def get_user_booking(session: AsyncSession, user: User) -> Booking | None:
    """Retrieves the current booking for a given user."""
    return await session.scalar(select(Booking).where(Booking.user_id == user.user_id))


async def get_available_slots(
    session: AsyncSession, user: User, target_date: datetime.date
) -> List[datetime.datetime]:
    """
    Generates a list of available 5-minute slots for a user on a specific date.
    """
    if not user.faculty:
        logger.error(
            f"User {user.telegram_id} has no faculty, cannot get window number."
        )
        return []

    window = user.faculty.window_number
    day_of_week = target_date.weekday()

    # 1. Get all time blocks for this window and day of the week
    stmt_slots = select(TimetableSlot).where(
        TimetableSlot.window_number == window,
        TimetableSlot.day_of_week == day_of_week,
        TimetableSlot.is_active == True,
    )
    result_slots = await session.scalars(stmt_slots)
    time_blocks = result_slots.all()

    # 2. Get all existing bookings for this window and date
    stmt_bookings = select(Booking.booking_datetime).where(
        Booking.window_number == window,
        func.date(Booking.booking_datetime) == target_date,
    )
    result_bookings = await session.scalars(stmt_bookings)
    booked_times = {b.replace(tzinfo=None) for b in result_bookings.all()}

    # 3. Generate all potential slots and filter out booked ones
    available_slots = []
    now = datetime.datetime.now()

    for block in time_blocks:
        current_time = datetime.datetime.combine(target_date, block.start_time)
        end_time = datetime.datetime.combine(target_date, block.end_time)

        while current_time < end_time:
            if current_time > now and current_time not in booked_times:
                available_slots.append(current_time)
            current_time += datetime.timedelta(minutes=5)

    return sorted(available_slots)


async def create_booking(
    session: AsyncSession, user: User, booking_datetime: datetime.datetime
) -> Tuple[Booking | None, str | None]:
    """Creates a booking for a user, returns booking object or error."""
    if user.is_signed_up:
        return None, "already_booked"

    # Check for race condition: re-verify the slot is free
    stmt = select(Booking).where(
        Booking.booking_datetime == booking_datetime,
        Booking.window_number == user.faculty.window_number,
    )
    existing_booking = await session.scalar(stmt)
    if existing_booking:
        return None, "too_late"  # Slot was just taken

    new_booking = Booking(
        user_id=user.user_id,
        booking_datetime=booking_datetime,
        window_number=user.faculty.window_number,
    )
    user.is_signed_up = True
    session.add(new_booking)
    session.add(user)
    await session.commit()
    return new_booking, None


async def cancel_booking(session: AsyncSession, user: User) -> Tuple[bool, str | None]:
    """Cancels a user's booking."""
    booking = await get_user_booking(session, user)
    if not booking:
        return False, "no_booking"

    # Check 3-hour rule
    time_difference = (
        booking.booking_datetime.replace(tzinfo=None) - datetime.datetime.now()
    )
    if time_difference < datetime.timedelta(hours=3):
        return False, "too_late"

    user.is_signed_up = False
    await session.delete(booking)
    session.add(user)
    await session.commit()
    return True, None

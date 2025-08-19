import datetime
from typing import List, Tuple

from loguru import logger
from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database.models import (
    Booking,
    Faculty,
    LastDay,
    ScheduleException,
    TimetableSlot,
    User,
)


async def get_user_booking(session: AsyncSession, user: User) -> Booking | None:
    """Retrieves the current booking for a given user."""
    return await session.scalar(select(Booking).where(Booking.user_id == user.user_id))


async def get_available_slots(
    session: AsyncSession, user: User, target_date: datetime.date
) -> List[datetime.datetime]:
    """
    Generates a list of available 5-minute slots for a user on a specific date,
    respecting the staggered window schedule (each window gets a slot every 15 minutes).
    """
    # --- Final validation layer ---
    last_day_record = await session.get(LastDay, 1)
    if not last_day_record or target_date > last_day_record.last_date:
        logger.warning(
            f"Attempted to get slots for an invalid date {target_date} "
            f"beyond last day {last_day_record.last_date if last_day_record else 'N/A'}"
        )
        return []
    # --- End validation ---

    if not user.faculty:
        logger.error(
            f"User {user.telegram_id} has no faculty, cannot get window number."
        )
        return []

    user_window = user.faculty.window_number
    day_of_week = target_date.weekday()

    # 1. Get all active time blocks for this day of the week FOR ALL WINDOWS.
    # We need all blocks to correctly calculate the staggered schedule.
    stmt_slots = select(TimetableSlot).where(
        TimetableSlot.day_of_week == day_of_week, TimetableSlot.is_active == True
    )
    result_slots = await session.scalars(stmt_slots)
    # Group blocks by start and end times to treat them as a single period for all windows
    time_blocks = {}
    for slot in result_slots.all():
        key = (slot.start_time, slot.end_time)
        if key not in time_blocks:
            time_blocks[key] = []
        time_blocks[key].append(slot)

    # 2. Get all existing bookings for the entire day to avoid conflicts
    stmt_bookings = select(Booking.booking_datetime).where(
        func.date(Booking.booking_datetime) == target_date,
    )
    result_bookings = await session.scalars(stmt_bookings)
    booked_times = {b.replace(tzinfo=None) for b in result_bookings.all()}

    # 3. Get all non-working exceptions for this date
    stmt_exceptions = select(ScheduleException).where(
        ScheduleException.exception_date == target_date,
        ScheduleException.is_working == False,
    )
    result_exceptions = await session.scalars(stmt_exceptions)
    exceptions = result_exceptions.all()

    # 4. Generate all potential slots and filter them
    available_slots = []
    now = datetime.datetime.now()

    # Sort blocks by start time to process them chronologically
    sorted_block_keys = sorted(time_blocks.keys())

    for start_t, end_t in sorted_block_keys:
        current_time = datetime.datetime.combine(target_date, start_t)
        end_time = datetime.datetime.combine(target_date, end_t)

        # The window cycle (1, 2, 3, 1, 2, 3...) resets for each major time block.
        window_cycle_counter = 0
        while current_time < end_time:
            # Determine which window's turn it is for this 5-minute slot
            current_window_turn = (window_cycle_counter % 3) + 1

            # A. Check if it's this user's window's turn
            if current_window_turn == user_window:
                # B. Check if this slot is inside any exception block for the target window
                is_blocked = False
                for exc in exceptions:
                    # Exception applies if it's for this specific window or for all windows (0)
                    if exc.window_number == user_window or exc.window_number == 0:
                        exc_start_dt = datetime.datetime.combine(
                            target_date, exc.start_time
                        )
                        exc_end_dt = datetime.datetime.combine(
                            target_date, exc.end_time
                        )
                        if exc_start_dt <= current_time < exc_end_dt:
                            is_blocked = True
                            break

                # C. Check if slot is available (in future, not booked, not blocked)
                if (
                    current_time > now
                    and current_time not in booked_times
                    and not is_blocked
                ):
                    available_slots.append(current_time)

            current_time += datetime.timedelta(minutes=5)
            window_cycle_counter += 1

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

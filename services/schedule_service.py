import datetime
from typing import Dict, List, Tuple

from loguru import logger
from sqlalchemy import and_, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database.models import Booking, LastDay, ScheduleException, TimetableSlot, User


async def get_user_booking(session: AsyncSession, user: User) -> Booking | None:
    """Retrieves the current booking for a given user."""
    return await session.scalar(select(Booking).where(Booking.user_id == user.user_id))


def _generate_staggered_slots(
    target_date: datetime.date,
    time_blocks: List[Dict[str, datetime.time]],
    start_window: int,
    user_window: int,
) -> List[datetime.datetime]:
    """Helper to generate staggered 5-minute slots based on a set of time blocks."""
    generated_slots = []
    now = datetime.datetime.now()

    sorted_blocks = sorted(time_blocks, key=lambda b: b["start"])

    for block in sorted_blocks:
        current_time = datetime.datetime.combine(target_date, block["start"])
        end_time = datetime.datetime.combine(target_date, block["end"])

        counter = 0
        while current_time < end_time:
            current_window_turn = ((start_window - 1 + counter) % 3) + 1
            if current_window_turn == user_window and current_time > now:
                generated_slots.append(current_time)
            current_time += datetime.timedelta(minutes=5)
            counter += 1
    return generated_slots


async def get_available_slots(
    session: AsyncSession, user: User, target_date: datetime.date
) -> List[datetime.datetime]:
    """
    Generates available slots using a unified exception-based system.
    1. Fetches all active exceptions for the target date.
    2. Checks for a high-priority 'non-working' rule.
    3. If no 'non-working' rule, gets the base schedule from TimetableSlots.
    4. Applies any 'modification' exceptions to the base schedule.
    5. Generates and filters slots based on the final, calculated schedule.
    """
    # --- Validation Layer ---
    last_day_record = await session.get(LastDay, 1)
    if not last_day_record or target_date > last_day_record.last_date:
        return []
    if not user.faculty:
        logger.error(f"User {user.telegram_id} has no faculty.")
        return []

    # 1. Fetch all active exceptions for the date, ordered by priority.
    stmt_exceptions = (
        select(ScheduleException)
        .where(
            ScheduleException.start_date <= target_date,
            ScheduleException.end_date >= target_date,
            ScheduleException.is_active == True,
        )
        .order_by(desc(ScheduleException.priority))
    )
    exceptions = (await session.scalars(stmt_exceptions)).all()

    # 2. Check for a 'non-working' rule. The highest priority one will be first.
    if any(e.is_non_working for e in exceptions):
        logger.debug(f"Date {target_date} is a non-working day due to an exception.")
        return []

    # 3. Get the base schedule from TimetableSlots FOR THE USER'S WINDOW.
    day_of_week = target_date.weekday()
    stmt_slots = select(TimetableSlot).where(
        TimetableSlot.day_of_week == day_of_week,
        TimetableSlot.is_active == True,
        TimetableSlot.window_number == user.faculty.window_number,
    )
    base_slots = await session.scalars(stmt_slots)

    # Prepare a mutable structure for the day's schedule
    time_blocks: List[Dict[str, datetime.time]] = [
        {"start": slot.start_time, "end": slot.end_time} for slot in base_slots
    ]
    start_window = 1  # Default start window

    # 4. Apply 'modification' exceptions that are relevant for this specific user.
    for exc in exceptions:
        # Rule is for specific years, and this user is not one of them. Skip.
        if exc.allowed_years and user.year not in exc.allowed_years:
            continue

        # Rule is for specific days, and this is not one of them. Skip.
        if exc.target_days_of_week and day_of_week not in exc.target_days_of_week:
            continue

        # Apply start window override from the highest priority applicable rule
        if exc.start_window_override is not None:
            start_window = exc.start_window_override
            logger.debug(f"Overriding start window to {start_window} for {target_date}")

        # Modify a specific time block
        if exc.target_start_time and exc.new_start_time and exc.new_end_time:
            for block in time_blocks:
                if block["start"] == exc.target_start_time:
                    logger.debug(f"Modifying slot {block['start']} on {target_date}")
                    block["start"] = exc.new_start_time
                    block["end"] = exc.new_end_time
                    break  # Assume one modifier per original slot time

    if not time_blocks:
        return []

    # 5. Generate and filter slots.
    potential_slots = _generate_staggered_slots(
        target_date=target_date,
        time_blocks=time_blocks,
        start_window=start_window,
        user_window=user.faculty.window_number,
    )

    stmt_bookings = select(Booking.booking_datetime).where(
        func.date(Booking.booking_datetime) == target_date,
    )
    booked_times = {
        b.replace(tzinfo=None) for b in (await session.scalars(stmt_bookings)).all()
    }
    available_slots = [slot for slot in potential_slots if slot not in booked_times]

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
    if await session.scalar(stmt):
        return None, "too_late"  # Slot was just taken

    new_booking = Booking(
        user_id=user.user_id,
        booking_datetime=booking_datetime,
        window_number=user.faculty.window_number,
    )
    user.is_signed_up = True
    session.add(new_booking)
    await session.commit()
    return new_booking, None


async def cancel_booking(session: AsyncSession, user: User) -> Tuple[bool, str | None]:
    """Cancels a user's booking."""
    booking = await get_user_booking(session, user)
    if not booking:
        return False, "no_booking"

    # Check 3-hour rule
    time_diff = booking.booking_datetime.replace(tzinfo=None) - datetime.datetime.now()
    if time_diff < datetime.timedelta(hours=3):
        return False, "too_late"

    user.is_signed_up = False
    await session.delete(booking)
    await session.commit()
    return True, None

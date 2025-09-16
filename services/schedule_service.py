import datetime
from typing import Dict, List, Tuple
from zoneinfo import ZoneInfo

from loguru import logger
from sqlalchemy import desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

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
    moscow_tz = ZoneInfo("Europe/Moscow")
    now_moscow = datetime.datetime.now(moscow_tz)

    sorted_blocks = sorted(time_blocks, key=lambda b: b["start"])

    for block in sorted_blocks:
        current_time = datetime.datetime.combine(
            target_date, block["start"], tzinfo=moscow_tz
        )
        end_time = datetime.datetime.combine(
            target_date, block["end"], tzinfo=moscow_tz
        )

        while current_time < end_time:
            if current_time > now_moscow:
                generated_slots.append(current_time)
            current_time += datetime.timedelta(minutes=5)
    return generated_slots


async def get_available_slots(
    session: AsyncSession, user: User, target_date: datetime.date
) -> List[datetime.datetime]:
    """
    Generates available slots using a unified exception-based system.
    """
    # --- Validation Layer ---
    last_day_record = await session.get(LastDay, 1)
    if not last_day_record or target_date > last_day_record.last_date:
        return []
    if not user.faculty:
        logger.error(f"User {user.telegram_id} has no faculty.")
        return []

    # 1. Fetch all active exceptions for the date, ordered by priority.
    day_of_week = target_date.weekday()
    stmt_exceptions = (
        select(ScheduleException)
        .where(
            ScheduleException.start_date <= target_date,
            or_(
                ScheduleException.end_date == None,  # noqa
                ScheduleException.end_date >= target_date,
            ),
            ScheduleException.is_active == True,
        )
        .order_by(desc(ScheduleException.priority))
    )
    exceptions = (await session.scalars(stmt_exceptions)).all()

    # 2. Preliminary check for 'exclusive' year-based rules.
    for exc in exceptions:
        if exc.block_others_if_years_mismatch and exc.allowed_years:
            if user.year not in exc.allowed_years:
                logger.debug(
                    f"User {user.telegram_id} blocked by exclusive year rule ID {exc.exception_id}"
                )
                return []

    # 3. Check for a 'non-working' rule.
    if any(e.is_non_working for e in exceptions):
        logger.debug(f"Date {target_date} is a non-working day due to an exception.")
        return []

    # 4. Get the base schedule and prepare for modifications.
    stmt_slots = select(TimetableSlot).where(
        TimetableSlot.day_of_week == day_of_week,
        TimetableSlot.is_active == True,
        TimetableSlot.window_number == user.faculty.window_number,
    )
    base_slots = await session.scalars(stmt_slots)

    time_blocks: List[Dict[str, datetime.time]] = [
        {"start": slot.start_time, "end": slot.end_time} for slot in base_slots
    ]
    start_window = 1

    # Apply 'modification' exceptions relevant for this user.
    for exc in exceptions:
        if exc.allowed_years and user.year not in exc.allowed_years:
            continue
        if exc.target_days_of_week and day_of_week not in exc.target_days_of_week:
            continue
        if exc.start_window_override is not None:
            start_window = exc.start_window_override
        if exc.target_start_time and exc.new_start_time and exc.new_end_time:
            for block in time_blocks:
                if block["start"] == exc.target_start_time:
                    block["start"] = exc.new_start_time
                    block["end"] = exc.new_end_time
                    break

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
    booked_times = set((await session.scalars(stmt_bookings)).all())
    available_slots = [slot for slot in potential_slots if slot not in booked_times]

    # Return naive datetime objects to the dialog for simplicity
    return sorted([slot.replace(tzinfo=None) for slot in available_slots])


async def create_booking(
    session: AsyncSession, user: User, booking_datetime: datetime.datetime
) -> Tuple[Booking | None, str | None, bool]:
    """
    Creates or updates a booking for a user.
    `booking_datetime` is expected to be a naive datetime from the dialog.
    """
    is_reschedule = False
    # The AwareDateTime type will handle conversion to UTC before saving
    if user.is_signed_up:
        is_reschedule = True
        old_booking = await get_user_booking(session, user)
        if old_booking:
            logger.info(
                f"User {user.telegram_id} is rescheduling. Deleting old booking {old_booking.booking_id}."
            )
            await session.delete(old_booking)
            await session.flush()
        else:
            logger.warning(
                f"User {user.telegram_id} has is_signed_up=True but no booking found."
            )

    # Re-verify the slot is free. AwareDateTime type handles timezone on booking_datetime.
    stmt = select(Booking).where(
        Booking.booking_datetime == booking_datetime,
        Booking.window_number == user.faculty.window_number,
    )
    if await session.scalar(stmt):
        return None, "too_late", is_reschedule

    new_booking = Booking(
        user_id=user.user_id,
        booking_datetime=booking_datetime,
        window_number=user.faculty.window_number,
    )
    user.is_signed_up = True
    session.add(new_booking)
    await session.commit()
    return new_booking, None, is_reschedule


async def cancel_booking(session: AsyncSession, user: User) -> Tuple[bool, str | None]:
    """Cancels a user's booking."""
    booking = await get_user_booking(session, user)
    if not booking:
        return False, "no_booking"

    # Check 3-hour rule. booking.booking_datetime is already in Moscow Time.
    time_diff = booking.booking_datetime - datetime.datetime.now(
        ZoneInfo("Europe/Moscow")
    )
    # Block cancellation only if the booking is in the future, but less than 3 hours away.
    if datetime.timedelta(0) < time_diff < datetime.timedelta(hours=3):
        return False, "too_late"

    user.is_signed_up = False
    await session.delete(booking)
    await session.commit()
    return True, None

import datetime
import os
from collections import defaultdict

import pandas as pd
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database.models import Booking, User
from lexicon import lexicon


async def generate_excel_report(session: AsyncSession, lang: str) -> str | None:
    """
    Generates an Excel report of all bookings.

    Args:
        session: The database session.
        lang: The language code for localization.

    Returns:
        The file path to the generated Excel file, or None if no data.
    """
    stmt = (
        select(Booking)
        .options(selectinload(Booking.user).selectinload(User.faculty))
        .order_by(Booking.booking_datetime)
    )
    result = await session.scalars(stmt)
    all_bookings = result.all()

    if not all_bookings:
        return None

    today = datetime.date.today()
    filename = f"booking_report_{today.isoformat()}.xlsx"

    # Group bookings by date using a more robust method
    bookings_by_date = defaultdict(list)
    for booking in all_bookings:
        bookings_by_date[booking.booking_datetime.date()].append(booking)

    with pd.ExcelWriter(filename, engine="openpyxl") as writer:
        # Sort dates to ensure sheets are in chronological order
        for date in sorted(bookings_by_date.keys()):
            bookings_on_day = bookings_by_date[date]
            sheet_name = date.strftime("%d-%m-%Y")

            # Sort bookings within the day by time and window
            sorted_bookings = sorted(
                bookings_on_day,
                key=lambda b: (b.booking_datetime.time(), b.window_number),
            )

            report_data = []
            for booking in sorted_bookings:
                user = booking.user
                if not user:  # Skip if the user was deleted
                    continue
                dt = booking.booking_datetime
                # Times for the report based on a 5-minute slot
                time1 = dt.strftime("%H:%M")
                time2 = (dt + datetime.timedelta(minutes=5)).strftime("%H:%M")
                time3 = (dt + datetime.timedelta(minutes=10)).strftime("%H:%M")

                report_data.append(
                    {
                        lexicon(lang, "report_header_window"): booking.window_number,
                        lexicon(lang, "report_header_room141"): time1,
                        lexicon(lang, "report_header_cashbox"): time2,
                        lexicon(lang, "report_header_room137"): time3,
                        lexicon(lang, "report_header_lastname"): user.last_name,
                        lexicon(lang, "report_header_firstname"): user.first_name,
                        lexicon(lang, "report_header_patronymic"): user.patronymic
                        or "",
                        lexicon(lang, "report_header_faculty"): (
                            user.faculty.name
                            if user.faculty
                            else lexicon(lang, "not_applicable")
                        ),
                        lexicon(lang, "report_header_degree"): lexicon(
                            lang, user.degree
                        ),
                        lexicon(lang, "report_header_year"): user.year,
                    }
                )

            if report_data:
                df = pd.DataFrame(report_data)
                df.to_excel(writer, sheet_name=sheet_name, index=False)

    return filename

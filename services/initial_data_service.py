import datetime

from loguru import logger
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from database.models import Faculty, LastDay, TimetableSlot

# Data based on the provided photo and old logic
FACULTIES_DATA = [
    {"name": "Биологический", "window_number": 1},
    {"name": "Психологический", "window_number": 1},
    {"name": "Исторический", "window_number": 1},
    {"name": "Философский", "window_number": 1},
    {"name": "ФФМ", "window_number": 2},
    {"name": "Географический", "window_number": 2},
    {"name": "Почвоведения", "window_number": 3},
    {"name": "Экономический", "window_number": 2},
    {"name": "ФББ", "window_number": 2},
    {"name": "ИСАА", "window_number": 2},
    {"name": "Журналистики", "window_number": 3},
    {"name": "Политологии", "window_number": 3},
    {"name": "ФФФХИ", "window_number": 3},
    {"name": "ВШКПиУ", "window_number": 3},
    # {"name": "ВШССН", "window_number": 3},
    {"name": "Другой", "window_number": 2},  # Added "Other" faculty
]


# Mon, Wed, Fri schedule (day_of_week 0, 2, 4)
WORKDAY_SCHEDULE = [
    {"start": "09:20", "end": "10:50"},
    {"start": "11:05", "end": "12:35"},
    {"start": "14:10", "end": "16:35"},
    {"start": "17:00", "end": "17:25"},
]

# Tue, Thu schedule (day_of_week 1, 3)
SHORT_DAY_SCHEDULE = [
    {"start": "09:20", "end": "10:50"},
    {"start": "11:05", "end": "12:35"},
]


async def populate_initial_faculties(session_maker: async_sessionmaker[AsyncSession]):
    """Populates the Faculty table with default data if it is empty."""
    async with session_maker() as session:
        try:
            result = await session.execute(select(func.count(Faculty.faculty_id)))
            if result.scalar_one() == 0:
                logger.info("Faculties table is empty. Populating...")
                new_faculties = [
                    Faculty(name=data["name"], window_number=data["window_number"])
                    for data in FACULTIES_DATA
                ]
                session.add_all(new_faculties)
                await session.commit()
                logger.info("Successfully populated faculties table.")
            else:
                logger.debug("Faculties table not empty. Skipping population.")
        except Exception:
            logger.exception("Error while populating faculties.")
            await session.rollback()


async def populate_initial_timetable(session_maker: async_sessionmaker[AsyncSession]):
    """Populates the TimetableSlot table with a default weekly schedule."""
    async with session_maker() as session:
        try:
            result = await session.execute(select(func.count(TimetableSlot.slot_id)))
            if result.scalar_one() == 0:
                logger.info("TimetableSlots table is empty. Populating...")
                new_slots = []
                for window in [1, 2, 3]:
                    # Mon, Wed, Fri
                    for day in [0, 2, 4]:
                        for block in WORKDAY_SCHEDULE:
                            new_slots.append(
                                TimetableSlot(
                                    day_of_week=day,
                                    start_time=datetime.time.fromisoformat(
                                        block["start"]
                                    ),
                                    end_time=datetime.time.fromisoformat(block["end"]),
                                    window_number=window,
                                )
                            )
                    # Tue, Thu
                    for day in [1, 3]:
                        for block in SHORT_DAY_SCHEDULE:
                            new_slots.append(
                                TimetableSlot(
                                    day_of_week=day,
                                    start_time=datetime.time.fromisoformat(
                                        block["start"]
                                    ),
                                    end_time=datetime.time.fromisoformat(block["end"]),
                                    window_number=window,
                                )
                            )
                session.add_all(new_slots)
                await session.commit()
                logger.info("Successfully populated timetable slots.")
            else:
                logger.debug("TimetableSlots table not empty. Skipping population.")
        except Exception:
            logger.exception("Error while populating timetable.")
            await session.rollback()


async def populate_initial_lastday(session_maker: async_sessionmaker[AsyncSession]):
    """Sets the initial last day for booking if not set."""
    async with session_maker() as session:
        try:
            last_day = await session.get(LastDay, 1)
            if not last_day:
                logger.info("LastDay not set. Populating with default value...")
                # Set default to end of next month
                today = datetime.date.today()
                first_day_of_current_month = today.replace(day=1)
                last_day_of_next_month = (
                    first_day_of_current_month + datetime.timedelta(days=62)
                ).replace(day=1) - datetime.timedelta(days=1)

                new_last_day = LastDay(id=1, last_date=last_day_of_next_month)
                session.add(new_last_day)
                await session.commit()
                logger.info(f"Set last booking date to {last_day_of_next_month}")
            else:
                logger.debug(f"Last booking date already set to {last_day.last_date}.")
        except Exception:
            logger.exception("Error while populating last day.")
            await session.rollback()

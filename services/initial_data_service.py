from loguru import logger
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from database.models import Faculty

# Data based on the provided photo
FACULTIES_DATA = [
    {"name": "Биологический", "window_number": 1},
    {"name": "Психологический", "window_number": 1},
    {"name": "Исторический", "window_number": 1},
    {"name": "Философский", "window_number": 1},
    {"name": "Географический", "window_number": 2},
    {"name": "Почвоведения", "window_number": 2},
    {"name": "Экономический", "window_number": 2},
    {"name": "ФББ", "window_number": 2},
    {"name": "ФФМ", "window_number": 2},
    {"name": "ВШГАИ", "window_number": 2},
    {"name": "ИСАА", "window_number": 2},
    {"name": "Журналистики", "window_number": 3},
    {"name": "Политологии", "window_number": 3},
    {"name": "ФФФХИ", "window_number": 3},
    {"name": "ВШКПиУ", "window_number": 3},
]


async def populate_initial_faculties(session_maker: async_sessionmaker):
    """
    Populates the Faculty table with default data if it is empty.
    """
    async with session_maker() as session:
        try:
            result = await session.execute(select(func.count(Faculty.faculty_id)))
            if result.scalar_one() == 0:
                logger.info("Faculties table is empty. Populating with initial data...")
                new_faculties = [
                    Faculty(name=data["name"], window_number=data["window_number"])
                    for data in FACULTIES_DATA
                ]
                session.add_all(new_faculties)
                await session.commit()
                logger.info("Successfully populated faculties table.")
            else:
                logger.debug(
                    "Faculties table already contains data. Skipping population."
                )
        except Exception as e:
            logger.exception("Error while populating initial faculties data.")
            await session.rollback()

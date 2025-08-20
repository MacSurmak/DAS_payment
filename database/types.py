from datetime import datetime
from zoneinfo import ZoneInfo

from sqlalchemy import DateTime, TypeDecorator

TARGET_TZ = ZoneInfo("Europe/Moscow")
DB_TZ = ZoneInfo("UTC")


class AwareDateTime(TypeDecorator):
    """
    Custom SQLAlchemy type to handle timezone-aware datetimes.

    - Stores all datetimes in the database as UTC.
    - When loading from the database, converts UTC time to the TARGET_TZ.
    - When saving to the database, converts the local time back to UTC.
    """

    impl = DateTime(timezone=True)
    cache_ok = True

    def process_bind_param(self, value: datetime | None, dialect) -> datetime | None:
        """On the way in (Python -> DB), convert to UTC."""
        if value is not None:
            if value.tzinfo is None:
                # Assume the naive datetime is in our target timezone
                value = value.replace(tzinfo=TARGET_TZ)
            return value.astimezone(DB_TZ)
        return value

    def process_result_value(self, value: datetime | None, dialect) -> datetime | None:
        """On the way out (DB -> Python), convert to TARGET_TZ."""
        if value is not None:
            # The value from DB is already timezone-aware (UTC)
            return value.astimezone(TARGET_TZ)
        return value

import datetime

from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Identity,
    Integer,
    String,
    Time,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .base import Base


class User(Base):
    """Represents a user of the bot."""

    __tablename__ = "users"

    user_id = Column(Integer, Identity(), primary_key=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False, index=True)
    first_name = Column(String(255))
    last_name = Column(String(255))
    patronymic = Column(String(255), nullable=True)
    faculty = Column(String(255))
    degree = Column(String(50))
    year = Column(Integer)
    is_admin = Column(Boolean, default=False, nullable=False)
    is_signed_up = Column(Boolean, default=False, nullable=False)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    booking = relationship("Booking", back_populates="user", uselist=False)

    def __repr__(self) -> str:
        return f"<User(id={self.user_id}, tg_id={self.telegram_id})>"


class Faculty(Base):
    """Represents a university faculty and its assigned window."""

    __tablename__ = "faculties"

    faculty_id = Column(Integer, Identity(), primary_key=True)
    name = Column(String(255), unique=True, nullable=False)
    window_number = Column(Integer, nullable=False)

    def __repr__(self) -> str:
        return f"<Faculty(id={self.faculty_id}, name='{self.name}', window={self.window_number})>"


class TimetableSlot(Base):
    """Represents a recurring, available slot in the weekly schedule."""

    __tablename__ = "timetable_slots"

    slot_id = Column(Integer, Identity(), primary_key=True)
    day_of_week = Column(Integer, nullable=False)  # Monday=0, Sunday=6
    start_time = Column(Time, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    window_number = Column(Integer, nullable=False)

    __table_args__ = (
        UniqueConstraint("day_of_week", "start_time", "window_number", name="uq_slot"),
    )

    def __repr__(self) -> str:
        return f"<TimetableSlot(id={self.slot_id}, day={self.day_of_week}, time='{self.start_time}')>"


class Booking(Base):
    """Represents a student's confirmed booking for a specific time slot."""

    __tablename__ = "bookings"

    booking_id = Column(Integer, Identity(), primary_key=True)
    user_id = Column(
        Integer, ForeignKey("users.user_id", ondelete="CASCADE"), unique=True
    )
    booking_datetime = Column(DateTime(timezone=True), nullable=False)
    window_number = Column(Integer, nullable=False)

    user = relationship("User", back_populates="booking")

    __table_args__ = (
        UniqueConstraint(
            "booking_datetime", "window_number", name="uq_booking_time_window"
        ),
    )

    def __repr__(self) -> str:
        return f"<Booking(id={self.booking_id}, user_id={self.user_id}, datetime='{self.booking_datetime}')>"

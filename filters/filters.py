from aiogram.filters import BaseFilter
from aiogram.types import CallbackQuery, Message
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import User


class IsRegistered(BaseFilter):
    """Checks if the user is registered in the database."""

    async def __call__(
        self, event: Message | CallbackQuery, session: AsyncSession
    ) -> bool:
        """
        Checks user registration.

        Args:
            event: The incoming event (Message or CallbackQuery).
            session: The database session.

        Returns:
            True if the user is registered, False otherwise.
        """
        user = await session.scalar(
            select(User).where(User.telegram_id == event.from_user.id)
        )
        return bool(user)

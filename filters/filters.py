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
        user = await session.scalar(
            select(User).where(User.telegram_id == event.from_user.id)
        )
        return bool(user)


class IsAdmin(BaseFilter):
    """Checks if the user is an administrator."""

    async def __call__(
        self, event: Message | CallbackQuery, session: AsyncSession
    ) -> bool:
        user = await session.scalar(
            select(User).where(User.telegram_id == event.from_user.id)
        )
        return bool(user and user.is_admin)

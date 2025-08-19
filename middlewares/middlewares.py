from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Update
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.orm import selectinload

from database import User
from lexicon import DEFAULT_LANG


class DbSessionMiddleware(BaseMiddleware):
    """Provides a database session to the handler."""

    def __init__(self, session_pool: async_sessionmaker[AsyncSession]):
        super().__init__()
        self.session_pool = session_pool

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        async with self.session_pool() as session:
            data["session"] = session
            return await handler(event, data)


class GetLangMiddleware(BaseMiddleware):
    """Determines the user's language and adds the user object to the data."""

    async def __call__(
        self,
        handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: Dict[str, Any],
    ) -> Any:
        session: AsyncSession = data["session"]
        user = data.get("event_from_user")
        lang_code = DEFAULT_LANG
        db_user = None

        if user:
            # Eagerly load the faculty and booking relationships
            stmt = (
                select(User)
                .where(User.telegram_id == user.id)
                .options(selectinload(User.faculty), selectinload(User.booking))
            )
            db_user = await session.scalar(stmt)
            if db_user:
                lang_code = db_user.lang if db_user.lang else DEFAULT_LANG
            elif user.language_code == "ru":
                lang_code = "ru"

        data["lang"] = lang_code
        data["user"] = db_user  # Add user object to data for easy access
        return await handler(event, data)

from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Update
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker

from database import User
from lexicon import DEFAULT_LANG


class DbSessionMiddleware(BaseMiddleware):
    """Provides a database session to the handler."""

    def __init__(self, session_pool: async_sessionmaker):
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
    """Determines the user's language and adds it to the data."""

    async def __call__(
        self,
        handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: Dict[str, Any],
    ) -> Any:
        session = data.get("session")
        user = data.get("event_from_user")
        lang_code = DEFAULT_LANG

        if user and session:
            db_user: User | None = await session.scalar(
                select(User).where(User.telegram_id == user.id)
            )
            if db_user and db_user.lang:
                lang_code = db_user.lang
            elif user.language_code == "ru":
                lang_code = "ru"

        data["lang"] = lang_code
        return await handler(event, data)

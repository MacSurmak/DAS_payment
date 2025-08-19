import time
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.types import Message, TelegramObject, Update
from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.orm import selectinload

from database.models import User
from lexicon import DEFAULT_LANG, lexicon


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


class MessageThrottlingMiddleware(BaseMiddleware):
    """Limits the frequency of messages from a user."""

    def __init__(self, storage: RedisStorage, rate_limit: float = 0.7):
        self.storage = storage
        self.rate_limit = rate_limit

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any],
    ) -> Any:
        user = data.get("event_from_user")
        if not user:
            return await handler(event, data)

        key = f"throttle:{user.id}"
        now = time.monotonic()
        last_time_str = await self.storage.redis.get(key)

        if last_time_str:
            try:
                last_time = float(last_time_str.decode())
                elapsed = now - last_time
                if elapsed < self.rate_limit:
                    lang = data.get("lang", DEFAULT_LANG)
                    warn_key = f"throttle_warn:{user.id}"
                    if not await self.storage.redis.get(warn_key):
                        await event.answer(lexicon(lang, "throttling_warning"))
                        await self.storage.redis.set(warn_key, "1", ex=5)
                    return
            except (ValueError, TypeError) as e:
                logger.error(f"Error decoding throttle time for user {user.id}: {e}")

        await self.storage.redis.set(key, str(now), ex=int(self.rate_limit * 2) + 1)
        return await handler(event, data)

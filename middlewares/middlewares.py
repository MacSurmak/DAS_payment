from typing import Any, Awaitable, Callable, Dict, Union
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery, TelegramObject
from aiogram.fsm.storage.redis import RedisStorage
from pyexpat.errors import messages

from lexicon.lexicon import lexicon


class MessageThrottlingMiddleware(BaseMiddleware):
    def __init__(self, storage: RedisStorage):
        self.storage = storage

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any],
    ) -> Any:

        user = str(event.from_user.id)
        check_user = await self.storage.redis.get(name=user)

        if check_user:
            if int(check_user.decode()) == 1:
                await self.storage.redis.set(name=user, value=2, ex=3)
                return await handler(event, data)
            elif int(check_user.decode()) == 2:
                await self.storage.redis.set(name=user, value=3, ex=10)
                return await event.answer(lexicon("throttling-warning"))
            elif int(check_user.decode()) == 3:
                return

        await self.storage.redis.set(name=user, value=1, ex=3)
        return await handler(event, data)

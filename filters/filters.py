from aiogram.filters import BaseFilter
from aiogram.types import CallbackQuery, Message

from database.crud import *


class IsAllowed(BaseFilter):
    async def __call__(self, message: Message = None, callback: CallbackQuery = None) -> bool:
        state = False
        for i in select_all_id():
            if str(message.chat.id) in i:
                state = True
        return state

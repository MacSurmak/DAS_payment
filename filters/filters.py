from aiogram.filters import BaseFilter
from aiogram.types import CallbackQuery, Message
from database.crud import *


class IsRegistered(BaseFilter):
    async def __call__(self, message: Message = None, callback: CallbackQuery = None) -> bool:
        state = False
        for i in read(table='Users',
                      columns='user_id'):
            if message.chat.id in i:
                state = True
        return state


class NoData(BaseFilter):
    async def __call__(self, message: Message = None, callback: CallbackQuery = None) -> bool:
        state = False
        if read(table='Users',
                columns='name',
                fetch=1)[0] is None:
            state = True
        return state


class IsSigned(BaseFilter):
    async def __call__(self, message: Message = None, callback: CallbackQuery = None) -> bool:
        state = False
        if read(table='Users',
                columns='signed',
                fetch=1)[0] == 1:
            state = True
        return state

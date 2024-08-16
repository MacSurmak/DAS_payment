from aiogram.filters import BaseFilter
from aiogram.types import CallbackQuery, Message
from database.crud import *


class IsRegistered(BaseFilter):
    async def __call__(self, message: Message = None, callback: CallbackQuery = None) -> bool:
        state = False
        for i in read(table='Users',
                      columns='user_id'):
            if message and message.chat.id in i:
                state = True
            elif callback and callback.message.chat.id in i:
                state = True
        return state


class NoName(BaseFilter):
    async def __call__(self, message: Message = None, callback: CallbackQuery = None) -> bool:
        state = False
        user_id = callback.message.chat.id if callback is not None else message.chat.id
        if read(table='Users',
                columns='name',
                user_id=user_id,
                fetch=1)[0] is None:
            state = True
        return state


class NoData(BaseFilter):
    async def __call__(self, message: Message = None, callback: CallbackQuery = None) -> bool:
        state = False
        user_id = callback.message.chat.id if callback is not None else message.chat.id
        if None in read(table='Users',
                        columns='faculty, degree, year',
                        user_id=user_id,
                        fetch=1):
            state = True
        return state


class IsSigned(BaseFilter):
    async def __call__(self, message: Message = None, callback: CallbackQuery = None) -> bool:
        state = False
        user_id = callback.message.chat.id if callback is not None else message.chat.id
        if read(table='Users',
                columns='signed',
                user_id=user_id,
                fetch=1)[0] == 1:
            state = True
        return state


class IsAdmin(BaseFilter):
    async def __call__(self, message: Message = None, callback: CallbackQuery = None) -> bool:
        state = False
        user_id = callback.message.chat.id if callback is not None else message.chat.id
        if read(table='Users',
                columns='admin',
                user_id=user_id,
                fetch=1) == (1,):
            state = True
        return state

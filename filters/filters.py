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


class IsRegistered(BaseFilter):
    async def __call__(self, message: Message = None, callback: CallbackQuery = None) -> bool:
        state = False
        for i in select_all_id():
            if message.chat.id in i:
                state = True
        return state


class NoData(BaseFilter):
    async def __call__(self, message: Message = None, callback: CallbackQuery = None) -> bool:
        state = False
        if select_data(message.chat.id)[0] is None:
            state = True
        return state


class IsSigned(BaseFilter):
    async def __call__(self, message: Message = None, callback: CallbackQuery = None) -> bool:
        state = False
        if select_signed(message.chat.id)[0] == 1:
            state = True
        return state

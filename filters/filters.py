from aiogram.filters import BaseFilter
from aiogram.types import Message

from database.crud import *


class IsRegistered(BaseFilter):
    async def __call__(self, message) -> bool:
        state = False
        if type(message) is Message:
            user_id = message.chat.id
        else:
            user_id = message.message.chat.id
        for i in read(table="Users", columns="user_id"):
            if user_id in i:
                state = True
        return state


class IsSigned(BaseFilter):
    async def __call__(self, message) -> bool:
        state = False
        if type(message) is Message:
            user_id = message.chat.id
        else:
            user_id = message.message.chat.id
        if read(table="Users", columns="signed", user_id=user_id, fetch=1) == (1,):
            state = True
        return state


class IsAdmin(BaseFilter):
    async def __call__(self, message) -> bool:
        state = False
        if type(message) is Message:
            user_id = message.chat.id
        else:
            user_id = message.message.chat.id
        if read(table="Users", columns="admin", user_id=user_id, fetch=1) == (1,):
            state = True
        return state

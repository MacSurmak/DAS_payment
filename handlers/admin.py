import re
import random
import hashlib
from msilib.schema import tables

from select import select

from config_data import config
from datetime import datetime, date, timedelta

from aiogram import Router, Bot
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, CallbackQuery

from database import last_day, timestamp
from database.crud import *
from filters.filters import IsRegistered, NoData, IsSigned, IsAdmin
from keyboards.commands_menu import yesno_markup, calendar_markup
from lexicon.lexicon import lexicon

router: Router = Router(name='admin-router')
router.message.filter(IsAdmin())


@router.message(Command('info'))
async def process_info_command(message: Message):
    """
    :param message: Telegram message
    """
    signed = len(read(table='Users',
                      signed=1))
    today = date.today()

    result = read(table='Lastday',
                  columns='month, day',
                  fetch=1)
    last_day = date(year=2024, month=result[0], day=result[1])
    vacant = 0
    while today <= last_day:
        vacant += len(read(table='Timetable',
                           signed=0,
                           month=today.month,
                           day=today.day))
        today += timedelta(days=1)

    await message.answer(text=lexicon('/info').format(signed=signed, vacant=vacant))

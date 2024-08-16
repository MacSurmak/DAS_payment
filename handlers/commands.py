import re
import random
from datetime import datetime

from aiogram import Router, Bot
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, CallbackQuery
from database.crud import *
from filters.filters import IsRegistered, NoData, IsSigned
from keyboards.commands_menu import yesno_markup, calendar_markup
from lexicon.lexicon import lexicon

router: Router = Router(name='commands-router')


@router.message(CommandStart(), ~IsRegistered())
async def process_start_command(message: Message):
    """
    :param message: Telegram message
    """
    user_id = message.from_user.id
    create(table='Users',
           user_id=user_id)
    await message.answer(text=lexicon('/start'))


@router.message(CommandStart(), IsRegistered(), NoData())
async def process_start_command(message: Message):
    """
    :param message: Telegram message
    """
    await message.answer(text=lexicon('/start-registered'))


@router.message(CommandStart(), IsRegistered(), ~NoData(), ~IsSigned())
async def process_start_command(message: Message):
    """
    :param message: Telegram message
    """
    window = read(table='Users',
                  columns='window',
                  user_id=message.chat.id,
                  fetch=1)[0]
    await message.answer(text=lexicon('ready').format(window=window),
                         reply_markup=calendar_markup(datetime.today().month))


@router.message(CommandStart(), IsRegistered(), ~NoData())
async def process_start_command(message: Message):
    """
    :param message: Telegram message
    """
    await message.answer(text=lexicon('/start-data').format(name=read(table='Users',
                                                                      columns='name',
                                                                      where='user_id={message.chat.id}')[0]))

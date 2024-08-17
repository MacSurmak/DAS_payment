import re
import random
import hashlib
from config_data import config
from datetime import datetime

from aiogram import Router, Bot
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, CallbackQuery
from database.crud import *
from filters.filters import IsRegistered, NoData, IsSigned, NoName, IsReady
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


@router.message(CommandStart(), IsRegistered(), NoName())
async def process_start_command(message: Message):
    """
    :param message: Telegram message
    """
    await message.answer(text=lexicon('/start-registered'))


@router.message(CommandStart(), IsRegistered(), NoData())
async def process_start_command(message: Message):
    """
    :param message: Telegram message
    """
    await message.answer(text=lexicon('/register'))


@router.message(CommandStart(), IsRegistered(), ~NoData(), ~IsSigned(), IsReady())
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
                                                                      user_id=message.chat.id,
                                                                      fetch=1)[0]))


@router.message(Command('admin'))
async def process_admin_command(message: Message):
    """
    :param message: Telegram message
    """
    try:
        password = message.text.split(' ')[1]
        hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
        if hash == config.bot.hash:
            await message.answer(text=lexicon('/admin-success'))
            update(table='Users',
                   admin=1,
                   where=f'user_id={message.chat.id}')
        else:
            await message.answer(text=lexicon('/admin-deny'))
    except IndexError:
        await message.answer(text=lexicon('/admin-no-pass'))


@router.message(Command('cancel'), IsSigned())
async def process_cancel_command(message: Message):
    """
    :param message: Telegram message
    """
    time = read(table='Timetable',
                columns='month, day, hour, minute',
                by_user=message.from_user.id,
                fetch=1)
    await message.answer(text=lexicon('/cancel').format(date=f'{str(time[0]).zfill(2)}.{str(time[1]).zfill(2)}',
                                                        time=f'{str(time[2]).zfill(2)}:{str(time[3]).zfill(2)}',
                                                        weekday=read(table='Timetable',
                                                                     columns='weekday',
                                                                     by_user=message.chat.id,
                                                                     fetch=1)[0]),
                         reply_markup=yesno_markup())

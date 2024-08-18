import hashlib
from datetime import datetime

from aiogram import Router
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State, default_state
from aiogram.types import Message

from config_data import config
from database.crud import *
from filters.filters import IsRegistered, IsSigned
from keyboards.commands_menu import yesno_markup, calendar_markup
from lexicon.lexicon import lexicon

router: Router = Router(name='commands-router')


class FSMRegistration(StatesGroup):
    name = State()
    faculty = State()
    degree = State()
    year = State()
    registered = State()
    sign = State()
    cancel = State()


@router.message(CommandStart(), ~IsRegistered())
async def process_start_command(message: Message, state: FSMContext):
    """
    :param message: Telegram message
    :param state: FSM state
    """
    user_id = message.from_user.id
    create(table='Users',
           user_id=user_id)
    await message.answer(text=lexicon('/start'))
    await state.set_state(FSMRegistration.name)


@router.message(CommandStart(), StateFilter(FSMRegistration.name))
async def process_start_command(message: Message):
    """
    :param message: Telegram message
    """
    await message.answer(text=lexicon('/start-registered'))


@router.message(CommandStart(), ~StateFilter(default_state, FSMRegistration.name, FSMRegistration.sign, FSMRegistration.cancel))
async def process_start_command(message: Message):
    """
    :param message: Telegram message
    """
    await message.answer(text=lexicon('/register'))


@router.message(CommandStart(), StateFilter(FSMRegistration.sign))
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


@router.message(CommandStart(), IsRegistered(), StateFilter(default_state, FSMRegistration.cancel))
async def process_start_command(message: Message):
    """
    :param message: Telegram message
    """
    timestamp = read(table = 'Timetable',
                     columns='month, day, hour, minute',
                     by_user = message.from_user.id,
                     fetch=1)
    window = read(table='Users',
                  columns='window',
                  user_id=message.chat.id,
                  fetch=1)[0]
    await message.answer(text=lexicon('signed2').format(date=f"{timestamp[1]} "
                                                             f"{lexicon(str(timestamp[0])).split(' ')[0]}",
                                                        time=f"{timestamp[2]}:{timestamp[3]}",
                                                        window=window,
                                                        weekday=read(table='Timetable',
                                                                     columns='weekday',
                                                                     by_user=message.chat.id,
                                                                     fetch=1)[0]),
                         reply_markup=None)
    # await message.answer(text=lexicon('/start-data').format(name=read(table='Users',
    #                                                                   columns='name',
    #                                                                   user_id=message.chat.id,
    #                                                                   fetch=1)[0]))


@router.message(Command('help'))
async def process_help_command(message: Message):
    """
    :param message: Telegram message
    """
    await message.answer(text=lexicon('/help'))


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
async def process_cancel_command(message: Message, state: FSMContext):
    """
    :param message: Telegram message
    :param state: FSM state
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
    await state.set_state(FSMRegistration.cancel)

import re
import random
from datetime import datetime, timedelta

from aiogram_calendar import SimpleCalendar, SimpleCalendarCallback, DialogCalendar, DialogCalendarCallback
from aiogram import Router, Bot
from aiogram import F
from aiogram.filters import Command, CommandStart
from aiogram.filters.callback_data import CallbackData
from aiogram.types import Message, CallbackQuery
from dateutil.rrule import weekday
from pandas.plotting import table

from database import window
from database.crud import *
from filters.filters import IsRegistered, NoData, NoName, IsSigned
from keyboards.commands_menu import yesno_markup, degree_markup, year_markup, faculty_markup, calendar_markup, \
    day_markup
from lexicon.lexicon import lexicon

router: Router = Router(name='messages-router')


@router.message(~IsRegistered())
async def process_registration(message: Message):
    """
    :param message: Telegram message
    """
    user_id = message.from_user.id
    create(table='Users',
           user_id=user_id)
    await message.answer(text=lexicon('/start'))


@router.message(IsRegistered(), NoName())
async def process_adding_data(message: Message):
    """
    :param message: Telegram message
    """
    if message.text:
        if message.text.replace(' ', '').isalpha():
            text = message.text.split()
            if len(text) in [2, 3]:
                surname = text[0]
                name = text[1]
                if len(text) == 3:
                    patronymic = text[2]
                else:
                    patronymic = '-'
                update(table='Users',
                       name=name,
                       surname=surname,
                       patronymic=patronymic,
                       where=f'user_id = {message.chat.id}')
                await message.answer(
                    text=lexicon('name-confirmation').format(name=name, surname=surname, patronymic=patronymic),
                    reply_markup=yesno_markup())
            elif len(text) == 1:
                await message.answer(text=lexicon('name-wrong2'),
                                     reply_markup=None)
            else:
                await message.answer(text=lexicon('name-wrong3'),
                                     reply_markup=None)
        else:
            await message.answer(text=lexicon('name-wrong'),
                                 reply_markup=None)
    else:
        await message.answer(text=lexicon('name-wrong4'),
                             reply_markup=None)


@router.callback_query(lambda callback: callback.data == '_no', NoData())
async def no(callback: CallbackQuery):
    """
    :param callback: Telegram callback
    """
    update(table='Users',
           name=None,
           surname=None,
           patronymic=None,
           where=f'user_id = {callback.message.chat.id}')
    await callback.message.edit_text(text=lexicon('repeat'),
                                     reply_markup=None)


@router.callback_query(lambda callback: callback.data == '_yes', NoData())
async def yes(callback: CallbackQuery):
    """
    :param callback: Telegram callback
    """
    text = callback.message.text.split('\n')
    surname = text[0].split(' ')[1]
    name = text[1].split(' ')[1]
    patronymic = text[2].split(' ')[1]
    update(table='Users',
           name=name,
           surname=surname,
           patronymic=patronymic,
           where=f'user_id = {callback.message.chat.id}')
    await callback.message.edit_text(text=lexicon('faculty').format(name=name),
                                     reply_markup=faculty_markup())


@router.callback_query(lambda callback: callback.data == 'back_degree')
async def yes(callback: CallbackQuery):
    """
    :param callback: Telegram callback
    """
    await callback.message.edit_text(text=lexicon('faculty_2'),
                                     reply_markup=faculty_markup())


@router.callback_query(lambda callback: callback.data.split('_')[0] == 'faculty')
async def faculty(callback: CallbackQuery):
    """
    :param callback: Telegram callback
    """
    faculty = lexicon(key=callback.data.split('_')[1])
    window = lexicon(faculty)
    update(table='Users',
           faculty=faculty,
           window=window,
           where=f'user_id={callback.message.chat.id}')
    await callback.message.edit_text(text=lexicon('accepted'),
                                     reply_markup=degree_markup())


@router.callback_query(lambda callback: callback.data == 'back_year')
async def yes(callback: CallbackQuery):
    """
    :param callback: Telegram callback
    """
    await callback.message.edit_text(text=lexicon('accepted_2'),
                                     reply_markup=degree_markup())


@router.callback_query(lambda callback: callback.data.split('_')[0] == 'degree')
async def bachelor(callback: CallbackQuery):
    """
    :param callback: Telegram callback
    """
    degree = lexicon(key=callback.data.split('_')[1])
    lengths = {
        'Бакалавриат': 4,
        'Магистратура': 2,
        'Специалитет': 6,
    }
    update(table='Users',
           degree=degree,
           where=f'user_id={callback.message.chat.id}')
    await callback.message.edit_text(text=lexicon('accepted'),
                                     reply_markup=year_markup(length=lengths[degree]))


@router.callback_query(lambda callback: callback.data.split('_')[1] == 'year')
async def aug(callback: CallbackQuery):
    """
    :param callback: Telegram callback
    """
    update(table='Users',
           year=callback.data.split('_')[0],
           where=f'user_id={callback.message.chat.id}')
    data = read(table='Users',
                columns='name, surname, patronymic, faculty, degree, year',
                user_id=callback.message.chat.id,
                fetch=1)
    await callback.message.edit_text(text=lexicon('confirm-data').format(name=data[0],
                                                                         surname=data[1],
                                                                         patronymic=data[2],
                                                                         faculty=data[3],
                                                                         degree=data[4],
                                                                         year=data[5]),
                                     reply_markup=yesno_markup())


@router.callback_query(lambda callback: callback.data == '_no', ~NoData(), ~IsSigned())
async def no(callback: CallbackQuery):
    """
    :param callback: Telegram callback
    """
    lengths = {
        'Бакалавриат': 4,
        'Магистратура': 2,
        'Специалитет': 6,
    }
    degree = read(table='Users',
                  columns='degree',
                  user_id=callback.message.chat.id,
                  fetch=1)[0]
    update(table='Users',
           year=None,
           where=f'user_id={callback.message.chat.id}')
    await callback.message.edit_text(text=lexicon('accepted'),
                                     reply_markup=year_markup(length=lengths[degree]))


@router.callback_query(lambda callback: callback.data == '_yes', ~NoData(), ~IsSigned())
async def yes(callback: CallbackQuery):
    """
    :param callback: Telegram callback
    """
    update(table='Users',
           ready=1,
           where=f'user_id={callback.message.chat.id}')
    window = read(table='Users',
                  columns='window',
                  user_id=callback.message.chat.id,
                  fetch=1)[0]
    await callback.message.edit_text(text=lexicon('ready').format(window=window),
                                     reply_markup=calendar_markup(datetime.today().month))


# @router.callback_query(lambda callback: callback.data.split('_')[1] == 'year')
# async def aug(callback: CallbackQuery):
#     """
#     :param callback: Telegram callback
#     """
#     window = read(table='Users',
#                   columns='window',
#                   user_id=callback.message.chat.id,
#                   fetch=1)[0]
#     update(table='Users',
#            year=callback.data.split('_')[0],
#            where=f'user_id={callback.message.chat.id}')
#     await callback.message.edit_text(text=lexicon('ready').format(window=window),
#                                      reply_markup=calendar_markup(datetime.today().month))


@router.callback_query(lambda callback: callback.data == 'calendar_back' or callback.data == 'back_to_calendar_8')
async def aug(callback: CallbackQuery):
    """
    :param callback: Telegram callback
    """
    window = read(table='Users',
                  columns='window',
                  user_id=callback.message.chat.id,
                  fetch=1)[0]
    await callback.message.edit_text(text=lexicon('ready').format(window=window),
                                     reply_markup=calendar_markup(8))


@router.callback_query(lambda callback: callback.data == 'calendar_next' or callback.data == 'back_to_calendar_9')
async def sep(callback: CallbackQuery):
    """
    :param callback: Telegram callback
    """
    window = read(table='Users',
                  columns='window',
                  user_id=callback.message.chat.id,
                  fetch=1)[0]
    await callback.message.edit_text(text=lexicon('ready').format(window=window),
                                     reply_markup=calendar_markup(9))


@router.callback_query(lambda callback: callback.data.split('_')[0] == 'day' and callback.data.split('_')[1] == 'yes')
async def day(callback: CallbackQuery):
    """
    :param callback: Telegram callback
    """
    window = read(table='Users',
                  columns='window',
                  user_id=callback.message.chat.id,
                  fetch=1)[0]
    await callback.message.edit_text(text=lexicon('ready').format(window=window),
                                     reply_markup=day_markup(callback.data.split('_')[2], window))


@router.callback_query(lambda callback: callback.data.split('_')[0] == 'day' and callback.data.split('_')[1] == 'no')
async def day(callback: CallbackQuery):
    """
    :param callback: Telegram callback
    """
    await callback.answer(text=lexicon('unavailable'), show_alert=True)


@router.callback_query(lambda callback: callback.data.split('_')[0] == 'time')
async def day(callback: CallbackQuery):
    """
    :param callback: Telegram callback
    """
    if read(table='Users',
            columns='signed',
            user_id=callback.message.chat.id,
            fetch=1)[0] == 1:
        await callback.answer(text=lexicon('already'), show_alert=True)
    else:
        timestamp = callback.data.split('_')[1].split(':')
        if read(table='Timetable',
                columns='signed',
                month=int(timestamp[0]),
                day=int(timestamp[1]),
                hour=int(timestamp[2]),
                minute=int(timestamp[3]),
                fetch=1)[0] == 1:
            await callback.answer(text=lexicon('already_time'), show_alert=True)
        else:
            window = read(table='Users',
                          columns='window',
                          user_id=callback.message.chat.id,
                          fetch=1)[0]
            update(table='Users',
                   signed=1,
                   where=f'user_id={callback.message.chat.id}')
            update(table='Timetable',
                   signed=1,
                   by_user=callback.message.chat.id,
                   where=f'month={int(timestamp[0])}, '
                         f'day={int(timestamp[1])}, '
                         f'hour={int(timestamp[2])}, '
                         f'minute={int(timestamp[3])}')
            await callback.message.edit_text(text=lexicon('signed').format(date=f'{timestamp[1]} '
                                                                                f'{lexicon(timestamp[0]).split(' ')[0]}',
                                                                           time=f'{timestamp[2]}:{timestamp[3]}',
                                                                           window=window,
                                                                           weekday=read(table='Timetable',
                                                                                        columns='weekday',
                                                                                        by_user=callback.message.chat.id,
                                                                                        fetch=1)[0]),
                                             reply_markup=None)


@router.message(IsSigned())
async def other(message: Message):
    """
    :param message: Telegram message
    """
    timestamp = read(table = 'Timetable',
                     columns='month, day, hour, minute',
                     by_user = message.from_user.id,
                     fetch=1)
    await message.answer(text=lexicon('signed2').format(date=f'{timestamp[1]} '
                                                             f'{lexicon(str(timestamp[0])).split(' ')[0]}',
                                                        time=f'{timestamp[2]}:{timestamp[3]}',
                                                        window=window,
                                                        weekday=read(table='Timetable',
                                                                     columns='weekday',
                                                                     by_user=message.chat.id,
                                                                     fetch=1)[0]),
                         reply_markup=None)


@router.callback_query(lambda callback: callback.data == '_no', IsSigned())
async def no(callback: CallbackQuery):
    """
    :param callback: Telegram callback
    """
    await callback.message.edit_text(text=lexicon('not-cancelled'),
                                     reply_markup=None)


@router.callback_query(lambda callback: callback.data == '_yes', IsSigned())
async def yes(callback: CallbackQuery):
    """
    :param callback: Telegram callback
    """
    update(table='Users',
           signed=0,
           where=f'user_id = {callback.message.chat.id}')
    update(table='Timetable',
           signed=0,
           by_user=None,
           where=f'by_user = {callback.message.chat.id}')
    await callback.message.edit_text(text=lexicon('cancelled'))


@router.message()
async def other(message: Message):
    """
    :param message: Telegram message
    """
    await message.answer(text=lexicon('reply-other'))

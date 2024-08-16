import calendar
from datetime import datetime, date

from aiogram_calendar import SimpleCalendar
from aiogram import Bot
from aiogram.types import BotCommand
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database.crud import *
from lexicon.lexicon import lexicon, LEXICON

from lexicon.lexicon import LEXICON_COMMANDS


async def set_commands_menu(bot: Bot):
    main_menu_commands = [BotCommand(
        command=command,
        description=description
    ) for command,
        description in LEXICON_COMMANDS.items()]
    await bot.set_my_commands(main_menu_commands)


def yesno_markup() -> InlineKeyboardMarkup:
    buttons: list[InlineKeyboardButton] = [
        InlineKeyboardButton(text=lexicon(key), callback_data=key) for key in ['_yes', '_no']
    ]
    kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
    kb_builder.row(*buttons, width=2)
    return kb_builder.as_markup(resize_keyboard=True)


def degree_markup() -> InlineKeyboardMarkup:
    buttons: list[InlineKeyboardButton] = [
        InlineKeyboardButton(text=lexicon(key), callback_data=f'degree_{key}') for key in ['bachelor', 'master', 'specialist']
    ]
    kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
    kb_builder.row(*buttons, width=2).row(InlineKeyboardButton(text=lexicon('back'), callback_data='back_degree'))
    return kb_builder.as_markup(resize_keyboard=True)


def year_markup(length) -> InlineKeyboardMarkup:
    buttons: list[InlineKeyboardButton] = [
        InlineKeyboardButton(text=f'{i + 1} курс', callback_data=f'{i + 1}_year') for i in range(length)
    ]
    kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
    kb_builder.row(*buttons, width=2).row(InlineKeyboardButton(text=lexicon('back'), callback_data='back_year'))
    return kb_builder.as_markup(resize_keyboard=True)


def faculty_markup() -> InlineKeyboardMarkup:
    buttons_long: list[InlineKeyboardButton] = [
        InlineKeyboardButton(text=lexicon(key), callback_data=f'faculty_{key}') for key in ['bio', 'geo', 'jou',
                                                                                            'ist', 'pol', 'soi',
                                                                                            'psy', 'phd', 'eco']
    ]
    buttons_short: list[InlineKeyboardButton] = [
        InlineKeyboardButton(text=lexicon(key), callback_data=f'faculty_{key}') for key in ['kpu', 'ssn', 'isa',
                                                                                            'fbb', 'ffm', 'fhi']
    ]
    kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
    kb_builder.row(*buttons_long, width=2).row(*buttons_short, width=3)
    return kb_builder.as_markup(resize_keyboard=True)

def calendar_markup(month) -> InlineKeyboardMarkup:
    kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
    kb_builder.row(InlineKeyboardButton(text=lexicon(month), callback_data='_empty'))
    buttons_weekdays: list[InlineKeyboardButton] = [
        InlineKeyboardButton(text=day, callback_data='_empty') for day in ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']
    ]
    kb_builder.row(*buttons_weekdays, width=7)

    obj = calendar.Calendar()
    days = obj.itermonthdates(2024, month)

    result = read(table='Lastday',
                  columns='month, day',
                  fetch=1)

    last_day = date(year=2024, month=result[0], day=result[1])

    buttons_days: list[InlineKeyboardButton] = []
    for day in days:
        if day.month == month:
            if day > last_day or day < date.today():
                sym = '✖'
                code = 'no'
            elif (0,) in read(table='Timetable',
                              columns='signed',
                              month=day.month,
                              day=day.day):
                sym = '✅'
                code = 'yes'
            else:
                sym = '✖'
                code = 'no'
            buttons_days.append(InlineKeyboardButton(text=str(day.day) + sym, callback_data=f'day_{code}_{day.day}-{day.month}'))
        else:
            buttons_days.append(InlineKeyboardButton(text=' ', callback_data=f'empty_{day}-{month}'))

    kb_builder.row(*buttons_days, width=7)

    if month == datetime.today().month:
        kb_builder.row(InlineKeyboardButton(text=lexicon('next'),
                                            callback_data=f'calendar_next'))
    else:
        kb_builder.row(InlineKeyboardButton(text=lexicon('back'),
                                            callback_data=f'calendar_back'))

    return kb_builder.as_markup(resize_keyboard=True)


def day_markup(timestamp, window) -> InlineKeyboardMarkup:
    day = int(timestamp.split('-')[0])
    month = int(timestamp.split('-')[1])

    kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
    kb_builder.row(InlineKeyboardButton(text=f'{day} {lexicon(f'{month}')}', callback_data='_empty'))

    times = read(table='Timetable',
                 columns='hour, minute, signed',
                 month=month,
                 day=day,
                 window=window)

    buttons_times: list[InlineKeyboardButton] = []

    for time in times:
        hour = time[0]
        minute = time[1]
        signed = time[2]

        if signed == 0:
            sym = '✅'
        else:
            sym = '✖'

        buttons_times.append(InlineKeyboardButton(text=f'{hour}:{minute if minute > 9 else f"0{minute}"}{sym}',
                                                  callback_data=f'time_{month}:{day}:{hour}:{minute if minute > 9 else f"0{minute}"}'))

    kb_builder.row(*buttons_times, width=3)

    kb_builder.row(InlineKeyboardButton(text=lexicon('back'),
                                        callback_data=f'back_to_calendar_{month}'))
    return kb_builder.as_markup(resize_keyboard=True)

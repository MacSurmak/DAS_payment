import os
import re
import random
import hashlib
import pandas as pd
from msilib.schema import tables

from select import select

from config_data import config
from datetime import datetime, date, timedelta

from aiogram import Router, Bot
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, CallbackQuery, FSInputFile

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


@router.message(Command('table'))
async def process_table_command(message: Message):
    """
    :param message: Telegram message
    """

    today = date.today()
    result = read(table='Lastday',
                  columns='month, day',
                  fetch=1)
    last_day = date(year=2024, month=result[0], day=result[1])

    filename = (f'Оплата запись с {str(today.day).zfill(2)}.{str(today.month).zfill(2)} '
                f'по {str(last_day.day).zfill(2)}.{str(last_day.month).zfill(2)}')
    
    with pd.ExcelWriter(f"{filename}.xlsx") as writer:
        while today <= last_day:
            day = read(table='Timetable',
                       month=today.month,
                       day=today.day)
            if day:

                timestamp = f'{day[0][2]} {lexicon(day[0][1])[0:3]}, {day[0][5]}'

                time1 = []
                for i in day:
                    time1.append(f'{i[3]}:{str(i[4]).zfill(2)}')

                time2 = []
                for i in day:
                    hour = i[3]
                    minute = i[4]+5
                    if minute >= 60:
                        minute -= 60
                        hour += 1
                    time2.append(f'{hour}:{str(minute).zfill(2)}')

                time3 = []
                for i in day:
                    hour = i[3]
                    i[4]+10
                    if minute >= 60:
                        minute -= 60
                        hour += 1
                    time3.append(f'{hour}:{str(minute).zfill(2)}')

                window = []
                for i in day:
                    window.append(f'Окно №{i[8]}')

                surname, name, patronymic, faculty, degree, year = [], [], [], [], [], []

                for i in day:
                    if i[7] is not None:

                        surname.append(read(table='Users',
                                            columns='surname',
                                            user_id=i[7],
                                            fetch=1)[0])

                        name.append(read(table='Users',
                                            columns='name',
                                            user_id=i[7],
                                            fetch=1)[0])

                        patronymic.append(read(table='Users',
                                            columns='patronymic',
                                            user_id=i[7],
                                            fetch=1)[0])

                        faculty.append(read(table='Users',
                                            columns='faculty',
                                            user_id=i[7],
                                            fetch=1)[0])

                        degree.append(read(table='Users',
                                            columns='degree',
                                            user_id=i[7],
                                            fetch=1)[0])

                        year.append(read(table='Users',
                                            columns='year',
                                            user_id=i[7],
                                            fetch=1)[0])

                    else:

                        surname.append('')
                        name.append('')
                        patronymic.append('')
                        faculty.append('')
                        year.append('')
                        degree.append('')


                # table = pd.DataFrame(day,
                #                      columns=['timestamp', 'month', 'day',
                #                               'hour', 'minute', 'weekday',
                #                               'signed', 'user', 'window'])

                table = pd.DataFrame()

                table['Окно'] = window
                table['141 каб.'] = time1
                table['Касса'] = time2
                table['137 каб.'] = time3
                table['Фамилия'] = surname
                table['Имя'] = name
                table['Отчество'] = patronymic
                table['Факультет'] = faculty
                table['Программа'] = degree
                table['Курс'] = year

                table.to_excel(writer, sheet_name=timestamp, index=False)

            today += timedelta(days=1)

    await message.answer_document(FSInputFile(f"{filename}.xlsx"))
    os.remove(f"{filename}.xlsx")


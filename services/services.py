from pandas.plotting import table
from select import select

from database.crud import *
from aiogram import Bot
import random
from datetime import datetime


async def notify_day_before(bot: Bot):

    dt = datetime.now()

    month = dt.month
    day = dt.day + 1
    hour = dt.hour
    minute = dt.minute

    signed_users = read(table='Users',
                        columns='user_id',
                        signed=1)

    for user in signed_users:
        time = read(table='Timetable',
                    columns='month, day, hour, minute',
                    by_user=user[0],
                    fetch=1)
        print(time)
        if time[0] == month and time[1] == day and time[2] == hour and time[3] == minute:
            await bot.send_message(chat_id=user[0],
                                   text='notif-day')


async def notify_hour_before(bot: Bot):

    dt = datetime.now()

    month = dt.month
    day = dt.day
    hour = dt.hour + 1
    minute = dt.minute

    signed_users = read(table='Users',
                        columns='user_id',
                        signed=1)

    for user in signed_users:
        time = read(table='Timetable',
                    columns='month, day, hour, minute',
                    by_user=user[0],
                    fetch=1)
        print(time)
        if time[0] == month and time[1] == day and time[2] == hour and time[3] == minute:
            await bot.send_message(chat_id=user[0],
                                   text='notif-hour')

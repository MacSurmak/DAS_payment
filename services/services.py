from datetime import datetime

from aiogram import Bot

from database.crud import *
from lexicon.lexicon import lexicon


async def notify_day_before(bot: Bot):

    dt = datetime.now()

    month = dt.month
    day = dt.day + 1
    hour = dt.hour
    minute = dt.minute

    signed_users = read(table='Users',
                        columns='user_id, window',
                        signed=1)

    for user in signed_users:
        time = read(table='Timetable',
                    columns='month, day, hour, minute',
                    by_user=user[0],
                    fetch=1)
        if time[0] == month and time[1] == day and time[2] == hour and time[3] == minute:
            await bot.send_message(chat_id=user[0],
                                   text=lexicon('notif-day').format(time=f'{time[2]}:{str(time[3]).zfill(2)}',
                                                                    window=user[1]))


async def notify_hour_before(bot: Bot):

    dt = datetime.now()

    month = dt.month
    day = dt.day
    hour = dt.hour + 1
    minute = dt.minute

    signed_users = read(table='Users',
                        columns='user_id, window',
                        signed=1)

    for user in signed_users:
        time = read(table='Timetable',
                    columns='month, day, hour, minute',
                    by_user=user[0],
                    fetch=1)
        if time[0] == month and time[1] == day and time[2] == hour and time[3] == minute:
            await bot.send_message(chat_id=user[0],
                                   text=lexicon('notif-hour').format(time=f'{time[2]}:{str(time[3]).zfill(2)}',
                                                                    window=user[1]))

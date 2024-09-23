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


async def send(bot: Bot):

    connection = sqlite3.connect('database/main.db')
    cursor = connection.cursor()

    cursor.execute(
        '''SELECT by_user FROM Timetable WHERE month = 9 AND weekday = 'Чт' AND day > 23 AND signed = 1 AND (timestamp LIKE '%w1%' OR timestamp LIKE '%w2%' OR timestamp LIKE '%w3%')''')
    fet = cursor.fetchall()
    ids = []
    for ent in fet:
        ids.append(ent[0])

    for user in ids:
        cursor.execute(
            '''UPDATE Timetable SET signed = 0 AND by_user = NULL WHERE by_user = ?''',
            (user,))
        cursor.execute(
            '''UPDATE Users SET signed = 0 WHERE user_id = ?''',
            (user,))

    connection.commit()
    connection.close()

    ids.append(391102946)
    for user in ids:
        await bot.send_message(chat_id=user,
                               text=lexicon('sorry'))

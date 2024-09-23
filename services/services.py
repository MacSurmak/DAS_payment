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

    ids = [864220392,
            1646505435,
            840675656,
            888603139,
            1942317820,
            656928668,
            1313375899,
            909712586,
            1266571539,
            874773157,
            1038859786,
            420334813,
            1304825749,
            532438186,
            1982736448,
            1435035857,
            607608788,
            1356580854,
            1061147659,
            1072091652,
            5173832582,
            1041360401,
            1194294959,
            356493119,
            586846289,
            1067838159,
            1292497490,
            1589412689,
            617738485,
            266410417,
            5261233061,
            308731945,
            756342700,
            984042932,
            743127014,
            847371938,
            718114190,
            5446946769,
            783617457,
            840210765,
            813546403,
            1914784293,
            886889341,
            1566532363]

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

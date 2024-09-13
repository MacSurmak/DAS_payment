import datetime
import sqlite3
from sqlite3 import IntegrityError

# Устанавливаем соединение с базой данных
connection = sqlite3.connect('database/main.db')
cursor = connection.cursor()

# Создаем таблицу Users
cursor.execute('''
CREATE TABLE IF NOT EXISTS Users (
user_id INTEGER PRIMARY KEY,
name TEXT,
surname TEXT,
patronymic TEXT,
faculty TEXT,
degree TEXT,
year INTEGER,
window INTEGER,
signed INTEGER DEFAULT '0',
admin INTEGER DEFAULT '0',
ready INTEGER DEFAULT '0'
)
''')

# Создаем таблицу Timetable
cursor.execute('''
CREATE TABLE IF NOT EXISTS Timetable (
timestamp TEXT PRIMARY KEY,
month INTEGER,
day INTEGER,
hour INTEGER,
minute INTEGER,
weekday TEXT,
signed INTEGER DEFAULT '0',
by_user INTEGER,
window INTEGER
)
''')

# Создаем таблицу Lastday
cursor.execute('''
CREATE TABLE IF NOT EXISTS Lastday (
id INTEGER PRIMARY KEY DEFAULT '1',
month INTEGER,
day INTEGER
)
''')

# try:
#     cursor.execute(
#                     'INSERT INTO Lastday (id, month, day) VALUES (?, ?, ?)',
#                     ('1', '8', '27',))
# except IntegrityError:
#      pass
#
# try:
#
#     week = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']
#
#     today = datetime.datetime(2024, 8, 20)
#     last_day = datetime.datetime(2024, 9, 30)
#
#     while today <= last_day:
#         if today.weekday() in [0, 2, 4] or today.month == 8:
#
#             time1 = today + datetime.timedelta(hours=9, minutes=20)
#             time2 = today + datetime.timedelta(hours=10, minutes=50)
#             time3 = today + datetime.timedelta(hours=11, minutes=5)
#             time4 = today + datetime.timedelta(hours=12, minutes=35)
#             window = 1
#
#             while time1 <= time2:
#                 timestamp = f'{today.month}.{today.day} {time1.hour}:{time1.minute if time1.minute > 9 else f"0{time1.minute}"}'
#                 cursor.execute('INSERT INTO Timetable (timestamp, month, day, hour, minute, weekday, window) '
#                                'VALUES (?, ?, ?, ?, ?, ?, ?)',
#                                (timestamp, today.month, today.day, time1.hour,
#                                 time1.minute, week[today.weekday()], window,))
#                 time1 += datetime.timedelta(minutes=5)
#                 if window < 3:
#                     window += 1
#                 else:
#                     window = 1
#
#             while time3 <= time4:
#                 timestamp = f'{today.month}.{today.day} {time3.hour}:{time3.minute if time3.minute > 9 else f"0{time3.minute}"}'
#                 cursor.execute('INSERT INTO Timetable (timestamp, month, day, hour, minute, weekday, window) '
#                                'VALUES (?, ?, ?, ?, ?, ?, ?)',
#                                (timestamp, today.month, today.day, time3.hour,
#                                 time3.minute, week[today.weekday()], window,))
#                 time3 += datetime.timedelta(minutes=5)
#                 if window < 3:
#                     window += 1
#                 else:
#                     window = 1
#
#             time1 = today + datetime.timedelta(hours=14, minutes=10)
#             time2 = today + datetime.timedelta(hours=16, minutes=35)
#             time3 = today + datetime.timedelta(hours=16, minutes=50)
#             time4 = today + datetime.timedelta(hours=17, minutes=20)
#
#             while time1 <= time2:
#                 timestamp = f'{today.month}.{today.day} {time1.hour}:{time1.minute if time1.minute > 9 else f"0{time1.minute}"}'
#                 cursor.execute('INSERT INTO Timetable (timestamp, month, day, hour, minute, weekday, window) VALUES (?, ?, ?, ?, ?, ?, ?)',
#                                (timestamp, today.month, today.day, time1.hour, time1.minute, week[today.weekday()], window))
#                 time1 += datetime.timedelta(minutes=5)
#                 if window < 3:
#                     window += 1
#                 else:
#                     window = 1
#
#             while time3 <= time4:
#                 timestamp = f'{today.month}.{today.day} {time3.hour}:{time3.minute if time3.minute > 9 else f"0{time3.minute}"}'
#                 cursor.execute('INSERT INTO Timetable (timestamp, month, day, hour, minute, weekday, window) VALUES (?, ?, ?, ?, ?, ?, ?)',
#                                (timestamp, today.month, today.day, time3.hour, time3.minute, week[today.weekday()], window))
#                 time3 += datetime.timedelta(minutes=5)
#                 if window < 3:
#                     window += 1
#                 else:
#                     window = 1
#
#         elif today.weekday() in [1, 3]:
#
#             time1 = today + datetime.timedelta(hours=9, minutes=20)
#             time2 = today + datetime.timedelta(hours=10, minutes=50)
#             time3 = today + datetime.timedelta(hours=11, minutes=5)
#             time4 = today + datetime.timedelta(hours=12, minutes=35)
#             window = 1
#
#             while time1 <= time2:
#                 timestamp = f'{today.month}.{today.day} {time1.hour}:{time1.minute if time1.minute > 9 else f"0{time1.minute}"}'
#                 cursor.execute('INSERT INTO Timetable (timestamp, month, day, hour, minute, weekday, window) '
#                                'VALUES (?, ?, ?, ?, ?, ?, ?)',
#                                (timestamp, today.month, today.day, time1.hour,
#                                 time1.minute, week[today.weekday()], window,))
#                 time1 += datetime.timedelta(minutes=5)
#                 if window < 3:
#                     window += 1
#                 else:
#                     window = 1
#
#             while time3 <= time4:
#                 timestamp = f'{today.month}.{today.day} {time3.hour}:{time3.minute if time3.minute > 9 else f"0{time3.minute}"}'
#                 cursor.execute('INSERT INTO Timetable (timestamp, month, day, hour, minute, weekday, window) '
#                                'VALUES (?, ?, ?, ?, ?, ?, ?)',
#                                (timestamp, today.month, today.day, time3.hour,
#                                 time3.minute, week[today.weekday()], window,))
#                 time3 += datetime.timedelta(minutes=5)
#                 if window < 3:
#                     window += 1
#                 else:
#                     window = 1
#
#         else:
#             pass
#
#         today += datetime.timedelta(days=1)
#
# except IntegrityError:
#      pass

week = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']

# today = datetime.datetime(year=2024, month=9, day=2)
# try:
#
#     while today <= datetime.datetime(year=2024, month=9, day=9):
#         if today.weekday() in [1, 3]:
#
#             time1 = today + datetime.timedelta(hours=14, minutes=10)
#             time2 = today + datetime.timedelta(hours=16, minutes=35)
#             time3 = today + datetime.timedelta(hours=16, minutes=50)
#             time4 = today + datetime.timedelta(hours=17, minutes=20)
#
#             window = 1
#
#             while time1 <= time2:
#                 timestamp = f'{today.month}.{today.day} {time1.hour}:{time1.minute if time1.minute > 9 else f"0{time1.minute}"}'
#                 cursor.execute('INSERT INTO Timetable (timestamp, month, day, hour, minute, weekday, window) '
#                                'VALUES (?, ?, ?, ?, ?, ?, ?)',
#                                (timestamp, today.month, today.day, time1.hour,
#                                 time1.minute, week[today.weekday()], window,))
#                 time1 += datetime.timedelta(minutes=5)
#                 if window < 3:
#                     window += 1
#                 else:
#                     window = 1
#
#             while time3 <= time4:
#                 timestamp = f'{today.month}.{today.day} {time3.hour}:{time3.minute if time3.minute > 9 else f"0{time3.minute}"}'
#                 cursor.execute('INSERT INTO Timetable (timestamp, month, day, hour, minute, weekday, window) '
#                                'VALUES (?, ?, ?, ?, ?, ?, ?)',
#                                (timestamp, today.month, today.day, time3.hour,
#                                 time3.minute, week[today.weekday()], window,))
#                 time3 += datetime.timedelta(minutes=5)
#                 if window < 3:
#                     window += 1
#                 else:
#                     window = 1
#
#         today += datetime.timedelta(days=1)
#
# except IntegrityError:
#      pass

today = datetime.datetime(year=2024, month=9, day=16)
try:

    while today <= datetime.datetime(year=2024, month=9, day=30):

        if today.weekday() in [1, 3]:

            time1 = today + datetime.timedelta(hours=15, minutes=00)
            time2 = today + datetime.timedelta(hours=16, minutes=35)
            time3 = today + datetime.timedelta(hours=16, minutes=50)
            time4 = today + datetime.timedelta(hours=17, minutes=25)

            while time1 <= time2:

                window = 1
                timestamp = f'{today.month}.{today.day} {time1.hour}:{time1.minute if time1.minute > 9 else f"0{time1.minute}"}'
                cursor.execute('INSERT INTO Timetable (timestamp, month, day, hour, minute, weekday, window) '
                           'VALUES (?, ?, ?, ?, ?, ?, ?)',
                           (timestamp, today.month, today.day, time1.hour,
                            time1.minute, week[today.weekday()], window,))

                window = 2
                timestamp = f'{today.month}.{today.day} {time1.hour}:{time1.minute if time1.minute > 9 else f"0{time1.minute}"} w{window}'
                cursor.execute('INSERT INTO Timetable (timestamp, month, day, hour, minute, weekday, window) '
                               'VALUES (?, ?, ?, ?, ?, ?, ?)',
                               (timestamp, today.month, today.day, time1.hour,
                                time1.minute, week[today.weekday()], window,))

                window = 3
                timestamp = f'{today.month}.{today.day} {time1.hour}:{time1.minute if time1.minute > 9 else f"0{time1.minute}"} w{window}'
                cursor.execute('INSERT INTO Timetable (timestamp, month, day, hour, minute, weekday, window) '
                               'VALUES (?, ?, ?, ?, ?, ?, ?)',
                               (timestamp, today.month, today.day, time1.hour,
                                time1.minute, week[today.weekday()], window,))

                time1 += datetime.timedelta(minutes=5)

            while time3 <= time4:
                window = 1
                timestamp = f'{today.month}.{today.day} {time1.hour}:{time1.minute if time1.minute > 9 else f"0{time1.minute}"}'
                cursor.execute('INSERT INTO Timetable (timestamp, month, day, hour, minute, weekday, window) '
                               'VALUES (?, ?, ?, ?, ?, ?, ?)',
                               (timestamp, today.month, today.day, time1.hour,
                                time1.minute, week[today.weekday()], window,))

                window = 2
                timestamp = f'{today.month}.{today.day} {time1.hour}:{time1.minute if time1.minute > 9 else f"0{time1.minute}"} w{window}'
                cursor.execute('INSERT INTO Timetable (timestamp, month, day, hour, minute, weekday, window) '
                               'VALUES (?, ?, ?, ?, ?, ?, ?)',
                               (timestamp, today.month, today.day, time1.hour,
                                time1.minute, week[today.weekday()], window,))

                window = 3
                timestamp = f'{today.month}.{today.day} {time1.hour}:{time1.minute if time1.minute > 9 else f"0{time1.minute}"} w{window}'
                cursor.execute('INSERT INTO Timetable (timestamp, month, day, hour, minute, weekday, window) '
                               'VALUES (?, ?, ?, ?, ?, ?, ?)',
                               (timestamp, today.month, today.day, time1.hour,
                                time1.minute, week[today.weekday()], window,))

                time3 += datetime.timedelta(minutes=5)

        elif today.weekday() in [0, 2, 4]:

            time1 = today + datetime.timedelta(hours=9, minutes=20)
            time2 = today + datetime.timedelta(hours=10, minutes=50)
            time3 = today + datetime.timedelta(hours=11, minutes=5)
            time4 = today + datetime.timedelta(hours=11, minutes=45)

            while time1 <= time2:

                window = 1
                timestamp = f'{today.month}.{today.day} {time1.hour}:{time1.minute if time1.minute > 9 else f"0{time1.minute}"}'
                cursor.execute('INSERT INTO Timetable (timestamp, month, day, hour, minute, weekday, window) '
                               'VALUES (?, ?, ?, ?, ?, ?, ?)',
                               (timestamp, today.month, today.day, time1.hour,
                                time1.minute, week[today.weekday()], window,))

                window = 2
                timestamp = f'{today.month}.{today.day} {time1.hour}:{time1.minute if time1.minute > 9 else f"0{time1.minute}"} w{window}'
                cursor.execute('INSERT INTO Timetable (timestamp, month, day, hour, minute, weekday, window) '
                               'VALUES (?, ?, ?, ?, ?, ?, ?)',
                               (timestamp, today.month, today.day, time1.hour,
                                time1.minute, week[today.weekday()], window,))

                window = 3
                timestamp = f'{today.month}.{today.day} {time1.hour}:{time1.minute if time1.minute > 9 else f"0{time1.minute}"} w{window}'
                cursor.execute('INSERT INTO Timetable (timestamp, month, day, hour, minute, weekday, window) '
                               'VALUES (?, ?, ?, ?, ?, ?, ?)',
                               (timestamp, today.month, today.day, time1.hour,
                                time1.minute, week[today.weekday()], window,))
                time1 += datetime.timedelta(minutes=5)

            while time3 <= time4:
                window = 1
                timestamp = f'{today.month}.{today.day} {time1.hour}:{time1.minute if time1.minute > 9 else f"0{time1.minute}"}'
                cursor.execute('INSERT INTO Timetable (timestamp, month, day, hour, minute, weekday, window) '
                               'VALUES (?, ?, ?, ?, ?, ?, ?)',
                               (timestamp, today.month, today.day, time1.hour,
                                time1.minute, week[today.weekday()], window,))

                window = 2
                timestamp = f'{today.month}.{today.day} {time1.hour}:{time1.minute if time1.minute > 9 else f"0{time1.minute}"} w{window}'
                cursor.execute('INSERT INTO Timetable (timestamp, month, day, hour, minute, weekday, window) '
                               'VALUES (?, ?, ?, ?, ?, ?, ?)',
                               (timestamp, today.month, today.day, time1.hour,
                                time1.minute, week[today.weekday()], window,))

                window = 3
                timestamp = f'{today.month}.{today.day} {time1.hour}:{time1.minute if time1.minute > 9 else f"0{time1.minute}"} w{window}'
                cursor.execute('INSERT INTO Timetable (timestamp, month, day, hour, minute, weekday, window) '
                               'VALUES (?, ?, ?, ?, ?, ?, ?)',
                               (timestamp, today.month, today.day, time1.hour,
                                time1.minute, week[today.weekday()], window,))
                time3 += datetime.timedelta(minutes=5)

            time1 = today + datetime.timedelta(hours=15, minutes=00)
            time2 = today + datetime.timedelta(hours=16, minutes=35)
            time3 = today + datetime.timedelta(hours=16, minutes=50)
            time4 = today + datetime.timedelta(hours=17, minutes=25)

            while time1 <= time2:
                window = 1
                timestamp = f'{today.month}.{today.day} {time1.hour}:{time1.minute if time1.minute > 9 else f"0{time1.minute}"}'
                cursor.execute('INSERT INTO Timetable (timestamp, month, day, hour, minute, weekday, window) '
                               'VALUES (?, ?, ?, ?, ?, ?, ?)',
                               (timestamp, today.month, today.day, time1.hour,
                                time1.minute, week[today.weekday()], window,))

                window = 2
                timestamp = f'{today.month}.{today.day} {time1.hour}:{time1.minute if time1.minute > 9 else f"0{time1.minute}"} w{window}'
                cursor.execute('INSERT INTO Timetable (timestamp, month, day, hour, minute, weekday, window) '
                               'VALUES (?, ?, ?, ?, ?, ?, ?)',
                               (timestamp, today.month, today.day, time1.hour,
                                time1.minute, week[today.weekday()], window,))

                window = 3
                timestamp = f'{today.month}.{today.day} {time1.hour}:{time1.minute if time1.minute > 9 else f"0{time1.minute}"} w{window}'
                cursor.execute('INSERT INTO Timetable (timestamp, month, day, hour, minute, weekday, window) '
                               'VALUES (?, ?, ?, ?, ?, ?, ?)',
                               (timestamp, today.month, today.day, time1.hour,
                                time1.minute, week[today.weekday()], window,))
                time1 += datetime.timedelta(minutes=5)

            while time3 <= time4:
                window = 1
                timestamp = f'{today.month}.{today.day} {time1.hour}:{time1.minute if time1.minute > 9 else f"0{time1.minute}"}'
                cursor.execute('INSERT INTO Timetable (timestamp, month, day, hour, minute, weekday, window) '
                               'VALUES (?, ?, ?, ?, ?, ?, ?)',
                               (timestamp, today.month, today.day, time1.hour,
                                time1.minute, week[today.weekday()], window,))

                window = 2
                timestamp = f'{today.month}.{today.day} {time1.hour}:{time1.minute if time1.minute > 9 else f"0{time1.minute}"} w{window}'
                cursor.execute('INSERT INTO Timetable (timestamp, month, day, hour, minute, weekday, window) '
                               'VALUES (?, ?, ?, ?, ?, ?, ?)',
                               (timestamp, today.month, today.day, time1.hour,
                                time1.minute, week[today.weekday()], window,))

                window = 3
                timestamp = f'{today.month}.{today.day} {time1.hour}:{time1.minute if time1.minute > 9 else f"0{time1.minute}"} w{window}'
                cursor.execute('INSERT INTO Timetable (timestamp, month, day, hour, minute, weekday, window) '
                               'VALUES (?, ?, ?, ?, ?, ?, ?)',
                               (timestamp, today.month, today.day, time1.hour,
                                time1.minute, week[today.weekday()], window,))
                time3 += datetime.timedelta(minutes=5)

        today += datetime.timedelta(days=1)

except IntegrityError:
     pass

# Сохраняем изменения и закрываем соединение
connection.commit()
connection.close()

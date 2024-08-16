import sqlite3
from calendar import month
from datetime import datetime, date


# def select(table, columns, where=''):
#
#     connection = sqlite3.connect('database/main.db')
#     cursor = connection.cursor()
#
#     if where:
#         params = where.split(', ')
#         where_str = '('
#         for param in range(len(params)):
#             where_str += params[param].split(' = ')[0]
#             if param < len(params) - 1:
#                 where_str += ', '
#         where_str += ') = ('
#         for param in range(len(params)):
#             where_str += '?'
#             if param < len(params) - 1:
#                 where_str += ', '
#         where_str += ')'
#         cursor.execute(f'SELECT {columns} FROM Users WHERE {where_str}')
#
#     results = cursor.fetchall()
#
#     connection.close()
#
#     return results


def select(table, columns, **where):

    connection = sqlite3.connect('database/main.db')
    cursor = connection.cursor()

    if where:
        params = '('
        values = ''
        values_list = ()
        for param, value in where:
            param += ', '
            params += param
            values += '?, '
            values_list += value
        params, values = params[:-2], values[:-2]
        params += ')'
        values += ')'

        cursor.execute(f'SELECT {columns} FROM Users WHERE {params} = {values}',
                       values_list)

    # if where:
    #     params = where.split(', ')
    #     where_str = '('
    #     for param in range(len(params)):
    #         where_str += params[param].split(' = ')[0]
    #         if param < len(params) - 1:
    #             where_str += ', '
    #     where_str += ') = ('
    #     for param in range(len(params)):
    #         where_str += '?'
    #         if param < len(params) - 1:
    #             where_str += ', '
    #     where_str += ')'
    #     cursor.execute(f'SELECT {columns} FROM Users WHERE {where_str}')

    results = cursor.fetchall()

    connection.close()

    return results


### Users

def insert_id(user_id):
    connection = sqlite3.connect('database/main.db')
    cursor = connection.cursor()

    cursor.execute('INSERT INTO Users (user_id) VALUES (?)',
                   (user_id,))

    connection.commit()
    connection.close()


def select_all_id():
    connection = sqlite3.connect('database/main.db')
    cursor = connection.cursor()

    cursor.execute('SELECT user_id FROM Users')
    results = cursor.fetchall()

    connection.close()

    return results


def select_data(user_id):
    connection = sqlite3.connect('database/main.db')
    cursor = connection.cursor()

    cursor.execute('SELECT name FROM Users WHERE user_id = ?', (user_id,))
    results = cursor.fetchone()

    connection.close()

    return results


def select_signed(user_id):
    connection = sqlite3.connect('database/main.db')
    cursor = connection.cursor()

    cursor.execute('SELECT signed FROM Users WHERE user_id = ?', (user_id,))
    results = cursor.fetchone()

    connection.close()

    return results


def select_window(user_id):
    connection = sqlite3.connect('database/main.db')
    cursor = connection.cursor()

    cursor.execute('SELECT window FROM Users WHERE user_id = ?', (user_id,))
    results = cursor.fetchone()

    connection.close()

    return results


def update_signed(value, user_id):
    connection = sqlite3.connect('database/main.db')
    cursor = connection.cursor()

    cursor.execute('UPDATE Users SET signed  = ? WHERE user_id = ?', (value, user_id,))

    connection.commit()
    connection.close()


def update_name(user_id, name, surname, patronymic):
    connection = sqlite3.connect('database/main.db')
    cursor = connection.cursor()

    cursor.execute('UPDATE Users SET (name, surname, patronymic) = (?, ?, ?) WHERE user_id = ?',
                   (name, surname, patronymic, user_id,))

    connection.commit()
    connection.close()


def update_degree(user_id, degree):
    connection = sqlite3.connect('database/main.db')
    cursor = connection.cursor()

    cursor.execute('UPDATE Users SET degree = ? WHERE user_id = ?',
                   (degree, user_id,))

    connection.commit()
    connection.close()


def update_year(user_id, year):
    connection = sqlite3.connect('database/main.db')
    cursor = connection.cursor()

    cursor.execute('UPDATE Users SET year = ? WHERE user_id = ?',
                   (year, user_id,))

    connection.commit()
    connection.close()


def update_faculty(user_id, faculty, window):
    connection = sqlite3.connect('database/main.db')
    cursor = connection.cursor()

    cursor.execute('UPDATE Users SET faculty = ?, window = ? WHERE user_id = ?',
                   (faculty, window, user_id,))

    connection.commit()
    connection.close()


# def delete(name, surname):
#     connection = sqlite3.connect('database/bitches.db')
#     cursor = connection.cursor()
#
#     cursor.execute('DELETE FROM Bitches WHERE name = ? AND surname = ?', (name, surname,))
#
#     connection.commit()
#     connection.close()


### Timetable

def select_time_signed(month, day, hour, minute):
    connection = sqlite3.connect('database/main.db')
    cursor = connection.cursor()

    cursor.execute('SELECT signed FROM Timetable WHERE (month, day, hour, minute) = (?, ?, ?, ?)',
                   (month, day, hour, minute,))
    results = cursor.fetchone()

    connection.close()

    return results


def select_whole_day_free(day, month):
    connection = sqlite3.connect('database/main.db')
    cursor = connection.cursor()

    cursor.execute('SELECT signed FROM Timetable WHERE (month, day) = (?, ?)',
                   (month, day))
    results = []
    for result in cursor.fetchall():
        results.append(result[0])

    connection.close()
    return results


def select_whole_day(day, month, window):
    connection = sqlite3.connect('database/main.db')
    cursor = connection.cursor()

    cursor.execute('SELECT hour, minute, signed FROM Timetable WHERE (month, day, window) = (?, ?, ?)',
                   (month, day, window))
    results = cursor.fetchall()

    connection.close()
    return results


def update_time(value, month, day, hour, minute, user_id):
    connection = sqlite3.connect('database/main.db')
    cursor = connection.cursor()

    cursor.execute('UPDATE Timetable SET (signed, by_user) = (?, ?) '
                   'WHERE (month, day, hour, minute) = (?, ?, ?, ?)', (value, user_id, month, day, hour, minute))

    connection.commit()
    connection.close()


### Admin

def select_last_day():
    connection = sqlite3.connect('database/main.db')
    cursor = connection.cursor()

    cursor.execute('SELECT month, day FROM Admin')
    results = cursor.fetchone()

    connection.close()

    return date(year=2024, month=results[0], day=results[1])



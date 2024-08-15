import sqlite3
from calendar import month
from datetime import datetime, date


def insert_id(user_id):
    connection = sqlite3.connect('database/main.db')
    cursor = connection.cursor()

    cursor.execute('INSERT INTO Users (user_id) VALUES (?)',
                   (user_id,))

    connection.commit()
    connection.close()


# def select(name, surname):
#     connection = sqlite3.connect('database/bitches.db')
#     cursor = connection.cursor()
#
#     cursor.execute('SELECT name, surname FROM Bitches WHERE name = ? AND surname = ?', (name, surname,))
#     results = cursor.fetchall()
#
#     connection.close()
#
#     return results
#
#
# def select_all():
#     connection = sqlite3.connect('database/bitches.db')
#     cursor = connection.cursor()
#
#     cursor.execute('SELECT name, surname, counter FROM Bitches')
#     results = cursor.fetchall()
#
#     connection.close()
#
#     return results
#
#
#
#
# def delete(name, surname):
#     connection = sqlite3.connect('database/bitches.db')
#     cursor = connection.cursor()
#
#     cursor.execute('DELETE FROM Bitches WHERE name = ? AND surname = ?', (name, surname,))
#
#     connection.commit()
#     connection.close()
#
#
# def insert_id(id):
#     connection = sqlite3.connect('database/bitches.db')
#     cursor = connection.cursor()
#
#     cursor.execute('INSERT INTO Registered (id) VALUES (?)',
#                    (id,))
#
#     connection.commit()
#     connection.close()
#
#
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


def select_time_signed(month, day, hour, minute):
    connection = sqlite3.connect('database/main.db')
    cursor = connection.cursor()

    cursor.execute('SELECT signed FROM Timetable WHERE (month, day, hour, minute) = (?, ?, ?, ?)',
                   (month, day, hour, minute,))
    results = cursor.fetchone()

    connection.close()

    return results


def update_signed(value, user_id):
    connection = sqlite3.connect('database/main.db')
    cursor = connection.cursor()

    cursor.execute('UPDATE Users SET signed  = ? WHERE user_id = ?', (value, user_id,))

    connection.commit()
    connection.close()


def update_time(value, month, day, hour, minute, user_id):
    connection = sqlite3.connect('database/main.db')
    cursor = connection.cursor()

    cursor.execute('UPDATE Timetable SET (signed, by_user) = (?, ?) '
                   'WHERE (month, day, hour, minute) = (?, ?, ?, ?)', (value, user_id, month, day, hour, minute))

    connection.commit()
    connection.close()


def select_window(user_id):
    connection = sqlite3.connect('database/main.db')
    cursor = connection.cursor()

    cursor.execute('SELECT window FROM Users WHERE user_id = ?', (user_id,))
    results = cursor.fetchone()

    connection.close()

    return results


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


def select_last_day():
    connection = sqlite3.connect('database/main.db')
    cursor = connection.cursor()

    cursor.execute('SELECT month, day FROM Admin')
    results = cursor.fetchone()

    connection.close()

    return date(year=2024, month=results[0], day=results[1])



import sqlite3
from datetime import date


def create(table, **kwargs):

    connection = sqlite3.connect('database/main.db')
    cursor = connection.cursor()

    params, values = '(', '('
    values_tuple = ()
    for param, value in kwargs.items():
        param += ', '
        params += param
        values += '?, '
        values_tuple += (value,)
    params, values = params[:-2], values[:-2]
    params += ')'
    values += ')'
    cursor.execute(f'INSERT INTO {table} {params} VALUES {values}',
                   values_tuple)

    connection.commit()
    connection.close()


def read(table, columns='*', fetch=-1, **kwargs):

    connection = sqlite3.connect('database/main.db')
    cursor = connection.cursor()

    if kwargs:
        params, values = '(', '('
        values_list = ()
        for param, value in kwargs.items():
            param += ', '
            params += param
            values += '?, '
            values_list += (value,)
        params, values = params[:-2], values[:-2]
        params += ')'
        values += ')'
        cursor.execute(f'SELECT {columns} FROM {table} WHERE {params} = {values}',
                       values_list)
    else:
        cursor.execute(f'SELECT {columns} FROM {table}')

    if fetch == 1:
        results = cursor.fetchone()
    elif fetch > 0:
        results = cursor.fetchmany(fetch)
    else:
        results = cursor.fetchall()

    connection.close()

    return results


def update(table, where, **kwargs):

    connection = sqlite3.connect('database/main.db')
    cursor = connection.cursor()

    params_set, values_set = '(', '('
    set_tuple = ()
    for param, value in kwargs.items():
        param += ', '
        params_set += param
        values_set += '?, '
        set_tuple += (value,)
    params_set, values_set = params_set[:-2], values_set[:-2]
    params_set += ')'
    values_set += ')'

    params_where, values_where = '(', '('
    values_tuple = ()
    where = where.replace(' ', '')
    for elem in where.split(','):
        param = elem.split('=')[0]
        value = elem.split('=')[1]
        param += ', '
        params_where += param
        values_where += '?, '
        values_tuple += (value,)
    params_where, values_where = params_where[:-2], values_where[:-2]
    params_where += ')'
    values_where += ')'

    cursor.execute(f'UPDATE {table} SET {params_set} = {values_set} WHERE {params_where} = {values_where}',
                   (set_tuple + values_tuple))

    connection.commit()
    connection.close()


def delete(table, **kwargs):

    connection = sqlite3.connect('database/main.db')
    cursor = connection.cursor()

    params, values = '(', '('
    values_tuple = ()
    for param, value in kwargs.items():
        param += ', '
        params += param
        values += '?, '
        values_tuple += (value,)
    params, values = params[:-2], values[:-2]
    params += ')'
    values += ')'
    cursor.execute(f'DELETE FROM {table} WHERE {params} = {values}',
                   values_tuple)

    connection.commit()
    connection.close()


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



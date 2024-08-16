import sqlite3


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

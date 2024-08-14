import sqlite3


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
# def update(counter, name, surname):
#     connection = sqlite3.connect('database/bitches.db')
#     cursor = connection.cursor()
#
#     cursor.execute('UPDATE Bitches SET counter = ? WHERE name = ? AND surname = ?',
#                    (counter, name, surname,))
#
#     connection.commit()
#     connection.close()
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
    print(results)

    connection.close()

    return results
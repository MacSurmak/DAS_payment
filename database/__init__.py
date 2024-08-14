import sqlite3

# Устанавливаем соединение с базой данных
connection = sqlite3.connect('database/users.db')
cursor = connection.cursor()

# Создаем таблицу Users
cursor.execute('''
CREATE TABLE IF NOT EXISTS Users (
id INTEGER PRIMARY KEY,
name TEXT,
surname TEXT,
patronymic TEXT,
faculty TEXT,
degree TEXT,
year INTEGER
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS Registered (
num INTEGER PRIMARY KEY,
id TEXT NOT NULL
)
''')

# Сохраняем изменения и закрываем соединение
connection.commit()
connection.close()

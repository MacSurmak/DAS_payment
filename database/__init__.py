import sqlite3

# Устанавливаем соединение с базой данных
connection = sqlite3.connect('database/bitches.db')
cursor = connection.cursor()

# Создаем таблицу Users
cursor.execute('''
CREATE TABLE IF NOT EXISTS Bitches (
id INTEGER PRIMARY KEY,
name TEXT NOT NULL,
surname TEXT NOT NULL,
counter INTEGER
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

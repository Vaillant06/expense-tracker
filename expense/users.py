import sqlite3

connection = sqlite3.connect('expense.db')
cursor = connection.cursor()
cursor.execute("DROP TABLE IF EXISTS users")
cursor.execute(
    '''CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        phone INTEGER UNIQUE NOT NULL,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        age INT REAL NOT NULL
        )
''')
connection.commit()
connection.close()

print("Users table created successfully")

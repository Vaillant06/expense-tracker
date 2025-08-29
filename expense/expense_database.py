import sqlite3

connection = sqlite3.connect('expense.db')
cursor = connection.cursor()
cursor.execute('''DROP TABLE IF EXISTS expenses''')
cursor.execute(
    '''CREATE TABLE IF NOT EXISTS expenses(
       id INTEGER PRIMARY KEY AUTOINCREMENT,
       title TEXT NOT NULL,
       amount REAL NOT NULL,
       category TEXT NOT NULL,
       date DATE NOT NULL,
       description TEXT
    )'''
)
connection.commit()
connection.close()

print("Database and table created successfully.")
# Expenses Database

import sqlite3

connection = sqlite3.connect('expense.db')
cursor = connection.cursor()
cursor.execute('''DROP TABLE IF EXISTS expenses''')
cursor.execute(
    '''CREATE TABLE IF NOT EXISTS expenses(
       id INTEGER PRIMARY KEY AUTOINCREMENT,
       user_id INTEGER NOT NULL,
       title TEXT NOT NULL,
       amount REAL NOT NULL,
       category TEXT NOT NULL,
       date DATE NOT NULL,
       description TEXT,
       FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    )'''
)
connection.commit()
connection.close()

print("Expenses table created successfully.")
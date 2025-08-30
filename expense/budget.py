import sqlite3

connection = sqlite3.connect('expense.db')
cursor = connection.cursor()
cursor.execute("DROP TABLE IF EXISTS budget")
cursor.execute(
    '''CREATE TABLE IF NOT EXISTS budget(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL UNIQUE,
        set_budget INT REAL NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    )'''
)
connection.commit()
connection.close()

print("Budget table created successfully")
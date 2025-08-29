from flask import Flask, render_template, redirect, url_for, request
import sqlite3
from datetime import datetime

app = Flask(__name__)

DB_NAME = "expense.db"

def get_db_connection():
    """Helper to open DB connection with row access by name"""
    connection = sqlite3.connect(DB_NAME)
    connection.row_factory = sqlite3.Row
    return connection


@app.route('/')
def home():
    with get_db_connection() as connection:
        cursor = connection.cursor()
        expenses = cursor.execute("SELECT * FROM expenses").fetchall()
        total = cursor.execute("SELECT SUM(amount) FROM expenses").fetchone()[0]
        if total is None: total = 0

    return render_template("home.html", expenses=expenses, total=total)


@app.route('/add_expense', methods=['GET', 'POST'])
def add_expense():
    if request.method == "POST":
        title = request.form['title']
        amount = request.form['amount']
        category = request.form['category']
        date = request.form['date']
        description = request.form['description']

        with get_db_connection() as connection:
            connection.execute(
                '''INSERT INTO expenses (title, amount, category, date, description)
                   VALUES (?, ?, ?, ?, ?)''',
                (title, amount, category, date, description)
            )
            connection.commit()

        return redirect(url_for('home'))

    today = datetime.utcnow().date().isoformat()
    return render_template("add_expense.html", today=today)

@app.route('/edit_expense/<int:id>', methods=['GET', 'POST'])
def edit_expense(id):
    connection = sqlite3.connect('expense.db')
    cursor = connection.cursor()
    if request.method == 'POST':
        title = request.form['title']
        amount = request.form['amount']
        category = request.form['category']
        date = request.form['date']
        description = request.form['description']

        cursor.execute('''
            UPDATE expenses
            SET title=?, amount=?, category=?, date=?, description=?
            WHERE id=?
        ''', (title, amount, category, date, description, id))
        connection.commit()
        connection.close()
        return redirect(url_for('home'))

    cursor.execute('SELECT * FROM expenses WHERE id=?', (id,))
    expense = cursor.fetchone()
    expense = list(expense)     
    expense_date = datetime.strptime(expense[4], "%d/%m/%Y").date()
    expense[4] = expense_date.isoformat()
    connection.commit()
    connection.close()

    return render_template('edit_expense.html', expense=expense, date=date)

@app.route('/delete_expense/<int:id>', methods=["POST"])
def delete_expense(id):
    with get_db_connection() as connection:
        connection.execute("DELETE FROM expenses WHERE id = ?", (id,))
        connection.commit()

    return redirect(url_for('home'))


if __name__ == "__main__":
    app.run(debug=True)

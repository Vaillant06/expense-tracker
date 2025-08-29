from flask import Flask, render_template, redirect, url_for, request
import sqlite3
from datetime import datetime, timezone

app = Flask(__name__)

DB_NAME = "expense.db"


# ------------------------
# Database Helper
# ------------------------
def get_db_connection():
    """Open DB connection with row access by name"""
    connection = sqlite3.connect(DB_NAME)
    connection.row_factory = sqlite3.Row
    return connection


# ------------------------
# Routes
# ------------------------
@app.route('/')
def home():
    with get_db_connection() as connection:
        cursor = connection.cursor()

        # Fetch all expenses
        expenses = cursor.execute("SELECT * FROM expenses").fetchall()

        # Calculate total spent
        total = cursor.execute("SELECT SUM(amount) FROM expenses").fetchone()[0] or 0

        # Group expenses by category
        cursor.execute("""
            SELECT category, SUM(amount) AS total
            FROM expenses
            GROUP BY category
        """)
        rows = cursor.fetchall()

    # Convert to dict: {category: total}
    categories_total = {
        row['category'] if row['category'] else "Uncategorized": row['total']
        for row in rows
    }

    # Ensure fixed categories exist even if empty
    categories = ['food', 'travel', 'clothes', 'academics', 'utilities', 'others']
    for cat in categories:
        categories_total.setdefault(cat, 0)

    return render_template("home.html", expenses=expenses, total=total, categories_total=categories_total)


@app.route('/add_expense', methods=['GET', 'POST'])
def add_expense():
    if request.method == "POST":
        data = {
            "title": request.form['title'],
            "amount": request.form['amount'],
            "category": request.form['category'],
            "date": request.form['date'],
            "description": request.form['description'],
        }

        with get_db_connection() as connection:
            connection.execute('''
                INSERT INTO expenses (title, amount, category, date, description)
                VALUES (:title, :amount, :category, :date, :description)
            ''', data)
            connection.commit()

        return redirect(url_for('home'))

    today = datetime.now(timezone.utc).date().isoformat()
    return render_template("add_expense.html", today=today)


@app.route('/edit_expense/<int:id>', methods=['GET', 'POST'])
def edit_expense(id):
    if request.method == "POST":
        data = {
            "title": request.form['title'],
            "amount": request.form['amount'],
            "category": request.form['category'],
            "date": request.form['date'],
            "description": request.form['description'],
            "id": id,
        }

        with get_db_connection() as connection:
            connection.execute('''
                UPDATE expenses
                SET title=:title, amount=:amount, category=:category, date=:date, description=:description
                WHERE id=:id
            ''', data)
            connection.commit()

        return redirect(url_for('home'))

    with get_db_connection() as connection:
        expense = connection.execute('SELECT * FROM expenses WHERE id=?', (id,)).fetchone()

    return render_template('edit_expense.html', expense=dict(expense))


@app.route('/delete_expense/<int:id>', methods=["POST"])
def delete_expense(id):
    with get_db_connection() as connection:
        connection.execute("DELETE FROM expenses WHERE id=?", (id,))
        connection.commit()

    return redirect(url_for('home'))


# ------------------------
# Main Entry
# ------------------------
if __name__ == "__main__":
    app.run(debug=True)

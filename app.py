from flask import Flask, session, render_template, redirect, url_for, request, flash
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timezone
import sqlite3  
from decimal import Decimal
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev_secret")
DB_NAME = "expense.db"


# ------------------------
#      Database Helper
# ------------------------

def get_db_connection():
    """Open DB connection with row access by name"""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


# ------------------------
#           Routes
# ------------------------

@app.route('/')
def dashboard():
    return render_template('dashboard.html')


# ------------------------
#         Register 
# ------------------------

@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form['username']
        age = request.form['age']
        raw_password = request.form['password']
        confirm_password = request.form['confirm-password']
        phone = request.form['phone']

        if raw_password != confirm_password:
            flash("Passwords do not match!", "error")
            return redirect(url_for('register'))

        with get_db_connection() as conn:
            if conn.execute("SELECT 1 FROM users WHERE username=?", (username,)).fetchone():
                flash("Username already exists!", "error")
                return redirect(url_for('register'))
            
            if conn.execute("SELECT 1 FROM users WHERE phone=?", (phone,)).fetchone():
                flash("Phone number exists!", "error")
                return redirect(url_for('register')) 

            hashed_pw = generate_password_hash(raw_password)
            conn.execute(
                "INSERT INTO users (username, phone, password, age) VALUES (?, ?, ?, ?)",
                (username, phone, hashed_pw, age),
            )
            conn.commit()

        flash("Registration successful!", "success")
        return redirect(url_for('login'))

    return render_template('register.html')


# ------------------------
#          Login 
# ------------------------
@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']

        with get_db_connection() as conn:
            user = conn.execute(
                "SELECT * FROM users WHERE username = ?", (username,)
            ).fetchone()

        if user and check_password_hash(user["password"], password): 
            session["user_id"] = user["id"]
            flash("Login successful!", "success")
            return redirect(url_for("profile"))

        flash("Invalid username or password!", "error")
        return redirect(url_for('login'))

    return render_template('login.html')


# ------------------------ 
#      User Dashboard
# ------------------------

@app.route('/user_dashboard')
def profile():
    if 'user_id' not in session:    
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    with get_db_connection() as conn:
        user = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        if not user:
            flash("User not found!", "error")
            return redirect(url_for('login'))

        budget_row = conn.execute(
            "SELECT set_budget FROM budget WHERE user_id = ?", (user_id,)
        ).fetchone()
        budget = budget_row[0] if budget_row else 0

        expenses = conn.execute(
            "SELECT * FROM expenses WHERE user_id = ? ORDER BY date DESC", (user_id,)
        ).fetchall()

        total = conn.execute(
            "SELECT SUM(amount) FROM expenses WHERE user_id = ?", (user_id,)
        ).fetchone()[0] or 0

        rows = conn.execute(
            """
            SELECT category, SUM(amount) 
            FROM expenses
            WHERE user_id = ?
            GROUP BY category
            """,
            (user_id,),
        ).fetchall()

    categories_total = {row[0] or "uncategorized": row[1] for row in rows}
    for cat in ['food', 'travel', 'clothes', 'academics', 'utilities', 'others']:
        categories_total.setdefault(cat, 0)

    remaining_budget = budget - total

    return render_template(
        "home.html",
        user_id=user['id'],
        username=user['username'],
        age=user['age'],
        phone=user['phone'],
        budget=budget,
        expenses=expenses,
        total=total,
        categories_total=categories_total,
        remaining_budget=remaining_budget
    )


# ------------------------
#        Set Budget 
# ------------------------

@app.route('/set_budget', methods=["POST"])
def set_budget():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    budget = request.form['budget']

    with get_db_connection() as conn:
        conn.execute(
            """
            INSERT INTO budget (user_id, set_budget)
            VALUES (?, ?)
            ON CONFLICT(user_id) DO UPDATE SET set_budget=excluded.set_budget
            """,
            (user_id, budget),
        )
        conn.commit()

    flash("Budget has been set successfully!", "success")
    return redirect(url_for('profile'))


# ------------------------
#       Update Budget
# ------------------------

@app.route('/update-budget/<int:user_id>', methods=['POST'])
def update_budget(user_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    new_budget = request.form['budget']
    with get_db_connection() as conn:
        old_budget_row = conn.execute(
            "SELECT set_budget FROM budget WHERE user_id=?", (user_id,)
        ).fetchone()
        old_budget = old_budget_row['set_budget'] if old_budget_row else None

        if old_budget is not None and str(new_budget) == str(old_budget):
            flash("Budget is not updated", "error")
            return redirect(url_for('profile'))

        conn.execute(
            """
            UPDATE budget
            SET set_budget=?
            WHERE user_id=?
            """, 
            (new_budget, user_id)
        )
        conn.commit()

    flash("Budget has been updated!", "success")
    return redirect(url_for('profile'))


# ------------------------ 
#         Edit Profile 
# ------------------------

@app.route('/edit_profile/<int:user_id>', methods=['POST'])
def edit_profile(user_id):
    if 'user_id' not in session:
        return redirect(url_for('login')) 

    data = (
        request.form['username'],
        request.form['phone_number'],
        request.form['age'],
        user_id
    )

    with get_db_connection() as conn:
        conn.execute(
            "UPDATE users SET username=?, phone=?, age=? WHERE id=?",
            data
        )
        conn.commit()

    flash("Profile has been updated successfully!", "success")
    return redirect(url_for('profile'))


# ------------------------ 
#         Add Expenses 
# ------------------------

@app.route('/add_expense', methods=['GET', 'POST'])
def add_expense():
    if 'user_id' not in session:
        flash("Login first!", "error")
        return redirect(url_for('login'))

    if request.method == "POST":
        data = {
            "user_id": session['user_id'],
            "title": request.form['title'],
            "amount": Decimal(request.form["amount"]),
            "category": request.form["category"],
            "date": request.form['date'],
            "description": request.form['description'],
        }

        with get_db_connection() as conn:
            conn.execute(
                """
                INSERT INTO expenses (user_id, title, amount, category, date, description)
                VALUES (:user_id, :title, :amount, :category, :date, :description)
                """,
                data,
            )
            conn.commit()

        flash("New expense added successfully!", "success")
        return redirect(url_for('profile'))

    today = datetime.now(timezone.utc).date().isoformat()
    return render_template("add_expense.html", today=today)


# ------------------------
#       Edit Expenses
# ------------------------

@app.route('/edit_expense/<int:id>', methods=['GET', 'POST'])
def edit_expense(id):
    if 'user_id' not in session:
        flash("Login first!", "error")
        return redirect(url_for('login'))

    with get_db_connection() as conn:
        if request.method == "POST":
            data = {
                "title": request.form['title'],
                "amount": request.form['amount'],
                "category": request.form['category'],
                "date": request.form['date'],
                "description": request.form['description'],
                "id": id,
                "user_id": session['user_id'],
            }
            conn.execute(
                """
                UPDATE expenses
                SET title=:title, amount=:amount, category=:category,
                    date=:date, description=:description
                WHERE id=:id AND user_id=:user_id
                """,
                data,
            )
            conn.commit()

            flash("Expense updated successfully!", "success")
            return redirect(url_for('profile'))

        expense = conn.execute(
            "SELECT * FROM expenses WHERE id=? AND user_id=?",
            (id, session['user_id']),
        ).fetchone()

    return render_template('edit_expense.html', expense=dict(expense))


# ------------------------
#      Delete Expenses
# ------------------------

@app.route('/delete_expense/<int:id>', methods=["POST"])
def delete_expense(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    with get_db_connection() as conn:
        conn.execute(
            "DELETE FROM expenses WHERE id=? AND user_id=?",
            (id, session['user_id']),
        )
        conn.commit()

    flash("Expense deleted successfully!", "success")
    return redirect(url_for('profile'))


# ------------------------ 
#          Logout 
# ------------------------

@app.route('/logout')
def logout():
    session.clear()
    flash("Logout Successful!", "success")
    return redirect(url_for('login'))


# ------------------------
#       Main Entry
# ------------------------
if __name__ == "__main__":
    app.run(debug=True)

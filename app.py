import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime

from helpers import login_required




# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///bookie.db")



@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/")
@login_required
def index():
    # If user session doesn't exist, redirect to login page, else redirect to index page
    if session.get("user_id") is None:
        return redirect("/login")
    else:
        return render_template("index.html")




@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return render_template("login.html", message="Please enter your username")

        # Ensure password was submitted
        elif not request.form.get("password"):
            return render_template("login.html", message="Please enter your password")

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return render_template("login.html", message="Invalid username and/or password")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]


        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return render_template("register.html", message="Please enter a username")

        # Ensure password was submitted
        elif not request.form.get("password"):
            return render_template("register.html", message="Please enter a password")

        # Ensure password confirmation was submitted
        elif not request.form.get("confirmation"):
            return render_template("register.html", message="Please confirm your password")

        # Ensure password and password confirmation match
        elif request.form.get("password") != request.form.get("confirmation"):
            return render_template("register.html", message="Passwords do not match")

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username does not already exist
        if len(rows) != 0:
            return render_template("register.html", message="Username already exists")

        # Insert user into database
        db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", request.form.get("username"), generate_password_hash(request.form.get("password")))

        # Redirect user to login form
        return redirect("/login")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/addbook", methods=["GET", "POST"])
@login_required
def addbook():
    """Add book to database"""
    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure title was submitted
        if not request.form.get("title"):
            # render boostrap toast error
            return render_template("/", message="Please enter a title")
            

        # Ensure author was submitted
        elif not request.form.get("author"):
            return render_template("/", message="Please enter an author")


        # Insert book into database
        # get current date and time
        

        db.execute("INSERT INTO books (title, author, date, user_id) VALUES (?, ?, ?, ?)", request.form.get("title"), request.form.get("author"), dt_string, session["user_id"])

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("/")

@app.route("/history", methods=["GET", "POST"])
@login_required
def history():
    
    # Select title, author and date from books table and merge with reviews for the book
    books = db.execute("SELECT books.title, books.author, books.date, reviews.review FROM books JOIN reviews ON books.id = reviews.book_id WHERE books.user_id = ?", session["user_id"])

    

    print(books)

    return render_template("history.html", books=books)

# sql command to add a new column to books table with status
# ALTER TABLE books ADD COLUMN status TEXT DEFAULT 'planned';

import os

import jsonify
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

status_list = ["Read", "To Read", "Reading", "Abandoned"]

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
        # Get user's books
        books = db.execute("SELECT * FROM books WHERE user_id = ?", session["user_id"])
        return render_template("index.html", books=books)




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

        # Get book status
        
        status = request.form['status']

        # Insert book into database
        db.execute("INSERT INTO books (title, author, date, user_id, status) VALUES (?, ?, ?, ?, ?)", request.form.get("title"), request.form.get("author"), dt_string, session["user_id"], status)

        # Redirect user to home page and send status_list to be shown in index.html
        return render_template("index.html")
        
    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("index.html")

@app.route("/history", methods=["GET", "POST"])
@login_required
def history():
    
    # Select title, author and date from books table and merge with reviews for the book
    books = db.execute("SELECT books.title, books.author, books.date, reviews.review FROM books JOIN reviews ON books.id = reviews.book_id WHERE books.user_id = ?", session["user_id"])

    return render_template("history.html", books=books)

# route to edit the book based on passed book id

editingBookID = 0
@app.route("/editbook/<int:book_id>", methods=["GET", "POST"])
@login_required
def editbook(book_id):
    #print(book_id)
    message = "Edit book details"
    # get book details from database
    book_data = db.execute("SELECT * FROM books WHERE id = ?", book_id)
    book = book_data[0]
    # TODO: book_id is passed, need to show the book details in the form
    #print(book)

    # global variable for remembering which book is being edited
    global editingBookID 
    editingBookID = book_id
    # render the editbook.html template with the current book id and book details
    
    return render_template("editbook.html", book=book, message=message)

@app.route("/editbooksave", methods=["GET", "POST"])
@login_required
def editbooksave():
    # get book details from the form
    # if no title is entered, show error
    # if request method is post
    book_data = db.execute("SELECT * FROM books WHERE id = ?", editingBookID)
    book = book_data[0]
    #print(book)
    if request.method == "POST":
        if not request.form.get("title"):
            return render_template("editbook.html", message="Please enter a title", book=book)
        # if no author is entered, show error
        if not request.form.get("author"):
            return render_template("editbook.html", message="Please enter an author", book=book)
        # verify that author is alphabetical, spaces allowed
        
        
        book_id = editingBookID
        title = request.form.get("title")
        author = request.form.get("author")
        status = request.form.get("status")

        #print(author)
        # update the book details in the database
        db.execute("UPDATE books SET title = ?, author = ?, status = ? WHERE id = ?", title, author, status, book_id)
        # redirect to the home page
        book_test = db.execute("SELECT * FROM books WHERE id = ?", book_id)
        print(book_test)
        books = db.execute("SELECT * FROM books WHERE user_id = ?", session["user_id"])
        return render_template("index.html", books=books)
    else:
        return render_template("index.html")



# sql command to add a new column to books table with status
# ALTER TABLE books ADD COLUMN status TEXT DEFAULT 'planned';

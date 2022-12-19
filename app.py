import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, jsonify
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime, timedelta

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
        number_of_read_books = db.execute("SELECT COUNT(*) FROM books WHERE user_id = ? AND status = ?", session["user_id"], "Read")
        number_of_to_read_books = db.execute("SELECT COUNT(*) FROM books WHERE user_id = ? AND status = ?", session["user_id"], "To Read")
        number_of_reading_books = db.execute("SELECT COUNT(*) FROM books WHERE user_id = ? AND status = ?", session["user_id"], "Reading")
        number_of_abandoned_books = db.execute("SELECT COUNT(*) FROM books WHERE user_id = ? AND status = ?", session["user_id"], "Abandoned")
        # adding each number of books to a list
        number_of_books = [number_of_read_books[0]["COUNT(*)"], number_of_to_read_books[0]["COUNT(*)"], number_of_reading_books[0]["COUNT(*)"], number_of_abandoned_books[0]["COUNT(*)"]]



        message = "Welcome to Bookie!"
        return render_template("index.html", books=books, message=message, number_of_books=number_of_books)




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
    # get current date and time, no seconds
    now = datetime.now()
    dt_string = now.strftime("%Y-%m-%d %H:%M")

    books = db.execute("SELECT * FROM books WHERE user_id = ?", session["user_id"])

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure title was submitted
        if not request.form.get("title"):
            # render boostrap toast error
            return render_template("index.html", message="Please enter a title", books=books)
            

        # Ensure author was submitted
        if not request.form.get("author"):
            return render_template("index.html", message="Please enter an author", books=books)

        if not request.form.get("status"):
            return render_template("index.html", message="Please select a status", books=books)
        # Get book status
        
        status = request.form['status']

        # Insert book into database
        db.execute("INSERT INTO books (title, author, date, user_id, status) VALUES (?, ?, ?, ?, ?)", request.form.get("title"), request.form.get("author"), dt_string, session["user_id"], status)

        # Redirect user to home page
        books = db.execute("SELECT * FROM books WHERE user_id = ?", session["user_id"])
        return render_template("index.html", books=books, message="Book added!")
        
    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("index.html", books=books)

@app.route("/reviews", methods=["GET", "POST"])
@login_required
def reviews():
    
    # Select title, author and date from books table and merge with reviews for the book
    books = db.execute("SELECT books.title, books.author, books.date, reviews.review FROM books JOIN reviews ON books.id = reviews.book_id WHERE books.user_id = ?", session["user_id"])

    return render_template("reviews.html", books=books)

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

    # global variable for remembering which book is being edited
    global editingBookID 
    editingBookID = book_id

    # get review from database for the book if it exists
    review_data = db.execute("SELECT * FROM reviews WHERE book_id = ?", book_id)
    if len(review_data) != 0:
        old_review = review_data[0]["review"]
    else:
        old_review = ""
    # render the editbook.html template with the current book id and book details
    
    
    # get book status from database
    status = book["status"]
    if status == "Reading":
        reading = "selected"
        read = ""
        to_read = ""
        abandoned = ""
    elif status == "Read":
        reading = ""
        read = "selected"
        to_read = ""
        abandoned = ""
    elif status == "To Read":
        reading = ""
        read = ""
        to_read = "selected"
        abandoned = ""
    elif status == "Abandoned":
        reading = ""
        read = ""
        to_read = ""
        abandoned = "selected"
    else:
        reading = ""
        read = ""
        to_read = ""
        abandoned = ""
    print(status)
    
    return render_template("editbook.html", book=book, message=message, old_review=old_review, reading=reading, read=read, to_read=to_read, abandoned=abandoned)

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
        
        book_id = editingBookID
        title = request.form.get("title")
        author = request.form.get("author")
        status = request.form.get("status")

        #print(author)
        # update the book details in the database
        db.execute("UPDATE books SET title = ?, author = ?, status = ? WHERE id = ?", title, author, status, book_id)

        books = db.execute("SELECT * FROM books WHERE user_id = ?", session["user_id"])

        # get review text from the form if it exists
        if request.form.get("review"):
            review = request.form.get("review")
            # if the review already exists, update it
            review_data = db.execute("SELECT * FROM reviews WHERE book_id = ?", book_id)
            if len(review_data) != 0:
                db.execute("UPDATE reviews SET review = ? WHERE book_id = ?", review, book_id)
            # if the review does not exist, insert it
            else:
                db.execute("INSERT INTO reviews (book_id, review) VALUES (?, ?)", book_id, review)
        return render_template("index.html", books=books, message="Book updated!")
    else:
        return render_template("index.html")


@app.route("/deletebook/<int:book_id>", methods=["GET", "POST"])
@login_required
def deletebook(book_id):
    # delete the book from the database
    db.execute("DELETE FROM books WHERE id = ?", book_id)
    # redirect to the index page
    books = db.execute("SELECT * FROM books WHERE user_id = ?", session["user_id"])
    return render_template("index.html", books=books, message="Book deleted!")
# sql command to add a new column to books table with status
# ALTER TABLE books ADD COLUMN status TEXT DEFAULT 'planned';


@app.route("/stats", methods=["GET", "POST"])
@login_required
def stats():
    # get the number of books read, reading, planned and abandoned
    read = db.execute("SELECT COUNT(*) FROM books WHERE user_id = ? AND status = ?", session["user_id"], "Read")
    reading = db.execute("SELECT COUNT(*) FROM books WHERE user_id = ? AND status = ?", session["user_id"], "Reading")
    planned = db.execute("SELECT COUNT(*) FROM books WHERE user_id = ? AND status = ?", session["user_id"], "To Read")
    abandoned = db.execute("SELECT COUNT(*) FROM books WHERE user_id = ? AND status = ?", session["user_id"], "Abandoned")
    # get the number of books read, reading and planned
    read = read[0]["COUNT(*)"]
    reading = reading[0]["COUNT(*)"]
    planned = planned[0]["COUNT(*)"]
    abandoned = abandoned[0]["COUNT(*)"]

    # monthly stats
    # get current month
    now = datetime.now()
    # dictionary for saving monthly stats
    monthly_stats = {}
    # get number of books read in the last 30 days
    read_this_month = db.execute("SELECT COUNT(*) FROM books WHERE user_id = ? AND status = ? AND date >= date('now', '-30 days')", session["user_id"], "Read")
    read_this_month = read_this_month[0]["COUNT(*)"]
    monthly_stats["read_this_month"] = read_this_month
    # get number of books reading in the last 30 days
    reading_this_month = db.execute("SELECT COUNT(*) FROM books WHERE user_id = ? AND status = ? AND date >= date('now', '-30 days')", session["user_id"], "Reading")
    reading_this_month = reading_this_month[0]["COUNT(*)"]
    monthly_stats["reading_this_month"] = reading_this_month
    # get number of books planned in the last 30 days
    planned_this_month = db.execute("SELECT COUNT(*) FROM books WHERE user_id = ? AND status = ? AND date >= date('now', '-30 days')", session["user_id"], "To Read")
    planned_this_month = planned_this_month[0]["COUNT(*)"]
    monthly_stats["planned_this_month"] = planned_this_month
    # get number of books abandoned in the last 30 days
    abandoned_this_month = db.execute("SELECT COUNT(*) FROM books WHERE user_id = ? AND status = ? AND date >= date('now', '-30 days')", session["user_id"], "Abandoned")
    abandoned_this_month = abandoned_this_month[0]["COUNT(*)"]
    monthly_stats["abandoned_this_month"] = abandoned_this_month
    # get total number of books in the last 30 days
    total_this_month = db.execute("SELECT COUNT(*) FROM books WHERE user_id = ? AND date >= date('now', '-30 days')", session["user_id"])
    total_this_month = total_this_month[0]["COUNT(*)"]
    monthly_stats["total_this_month"] = total_this_month


    print("read: ", read)
    print("reading: ", reading)
    print("planned: ", planned)
    print("abandoned: ", abandoned)
    
    

    # get the number of books read, reading and planned
    total = read + reading + planned + abandoned
    # calculate the percentage of books read, reading and planned
    read_percent = round(read / total * 100)
    reading_percent = round(reading / total * 100)
    planned_percent = round(planned / total * 100)
    abandoned_percent = round(abandoned / total * 100)

    


    message_goals = "No goal set yet"
    goal = 0
    # get the goal
    goal_data = db.execute("SELECT * FROM goals WHERE user_id = ?", session["user_id"])
    if len(goal_data) != 0:
        goal = goal_data[0]["goal"]
        # calculate the percentage of books read, reading and planned
        goal_percent = round(int(read_this_month) / int(goal) * 100)
        print("goal percent: ", goal_percent)
        message_goals = str(read_this_month) + "/" + str(goal)
    else:
        goal_percent = 0
        message_goals = "No goal set yet"

    

    # render the stats.html template with the stats
    return render_template("stats.html", read=read, reading=reading, planned=planned, read_percent=read_percent, reading_percent=reading_percent, planned_percent=planned_percent, abandoned_percent=abandoned_percent, abandoned=abandoned, total=total, monthly_stats=monthly_stats, message_goals=message_goals, goal_percent=goal_percent)

@app.route("/setgoal", methods=["GET", "POST"])
@login_required
def setgoal():
    # get the goal
    if request.form.get("goal"):
        goal = request.form.get("goal")
        # if the goal already exists, update it
        goal_data = db.execute("SELECT * FROM goals WHERE user_id = ?", session["user_id"])
        if len(goal_data) != 0:
            now = datetime.now()
            date = now.strftime("%Y-%m-%d")
            # update goals with the new goal and date
            db.execute("UPDATE goals SET goal = ?, date = ? WHERE user_id = ?", goal, date, session["user_id"])
            
        # if the goal does not exist, insert it
        else:
            # get today's date
            now = datetime.now()
            date = now.strftime("%Y-%m-%d")

            db.execute("INSERT INTO goals (user_id, goal, date) VALUES (?, ?, ?)", session["user_id"], goal, date)
        # redirect to the stats page
        return redirect("/stats")
    else:
        return render_template("setgoal.html")

@app.route("/search")
@login_required
def search():
    
    query = request.args.get("q")
    # select all books that match the query
    if query:
        books = db.execute("SELECT * FROM books WHERE title COLLATE NOCASE LIKE ? OR author LIKE ?", "%" + query + "%", "%" + query + "%")
    else:
        books = []
    return jsonify(books)
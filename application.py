import os

from flask import Flask, session, render_template, request, redirect, url_for
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps
import requests

app = Flask(__name__)
# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))




@app.route("/")
def index():
    #Redirects user to the login screen if they are not yet logged in 
    if not session.get("user_id"):
        return redirect("/login")
    else:
        return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    session.clear()

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirm = request.form.get("confirm")
        name = request.form.get("name")


        #Check to see if username is already registered
        users = db.execute("SELECT * FROM users WHERE username = :username", {"username": username})
        user = users.fetchone()
        if user:
            return render_template("invalid.html", error_message="That username already exists!", redirect="/register")
        
        #Check to see if any fields were left empty
        elif not request.form.get("username"):
            return render_template("invalid.html", error_message="Please enter a username", redirect="/register")

        elif not request.form.get("password"):
            return render_template("invalid.html", error_message="Please enter a password", redirect="/register")

        elif not request.form.get("confirm"):
            return render_template("invalid.html", error_message="Please confirm your password", redirect="/register")

        #Checks to see if password matches confirmation
        elif password != confirm:
            return render_template("invalid.html", error_message="Passwords do not match", redirect="/register")

        #Adds new user to database
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)
        db.execute("INSERT INTO users (username, password, name) VALUES (:username, :password, :name)",
                    {"username": username, "password": hashed_password, "name": name})
        db.commit()
        return render_template("success.html")
    
    elif request.method == "GET":
        return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        users = db.execute("SELECT * FROM users WHERE username = :username", {"username": username})
        user = users.fetchone()

        if user == None or not check_password_hash(user[2], password):
            return render_template("invalid.html", error_message="Invalid username or password", redirect="/login")

        #Updates session user ID and username after successful login and redirects to homepage
        session["user_id"] = user[0]
        session["user_name"] = user[1]
        return redirect("/")




    elif request.method == "GET":
        return render_template("login.html")


@app.route("/search", methods=["GET"])
def search():
    searchText = request.args.get("book-search")
    query = "%" + searchText + "%"
    query = query.title()
    
    results = db.execute("SELECT * FROM books WHERE isbn LIKE :query OR title LIKE :query OR author LIKE :query LIMIT 10", {"query": query})
    if(results.rowcount == 0):
        return render_template("invalid.html", error_message="Error: No books found with those search parameters.", redirect="/")

    matches = results.fetchall()

    return render_template("results.html", matches=matches)


@app.route("/book/<isbn>", methods=["GET", "POST"])
def book(isbn):

    #Display book page if request method is GET
    if request.method == "GET":
        if not session.get("user_id"):
            return redirect("/login")

        book = db.execute("SELECT * FROM books WHERE isbn=:isbn", {"isbn":isbn}).fetchone()
        if book == None:
            return render_template("invalid.html", error_message="Error: No such book with ISBN found", redirect="/")

        book_id = book['book_id']
        reviews = db.execute("SELECT * FROM reviews WHERE book_id=:book_id", {"book_id":book_id})

        isbn=str(isbn)
        res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "I6f1Rt4i8e2CIWH11kKJA", "isbns": isbn})
        data=res.json()
        avg_rating = data["books"][0]["average_rating"]
        num_ratings=data["books"][0]["work_ratings_count"]

    

        return render_template("book.html", book=book, avg_rating=avg_rating, num_ratings=num_ratings, reviews=reviews)

    #Upload review if request method is POST
    elif request.method=="POST":

        isbn=str(isbn)
        user_id = session.get("user_id")
        rating = request.form.get("score")
        review = request.form.get("review")
        review = str(review)
        book = db.execute("SELECT book_id FROM books WHERE isbn=:isbn", {"isbn":isbn})
        book_id = book.fetchone()
        book_id = book_id[0]

        rating = int(rating)
        book_id=int(book_id)
        user_id=int(user_id)
        db.execute("INSERT INTO reviews (review, user_id, book_id, rating) VALUES (:review, :user_id, :book_id, :rating)", {"review":review, "user_id":user_id, "book_id":book_id, "rating": rating})
        db.commit()

        return redirect("/")

    
@app.route("/logout", methods=["GET"])
def logout():
    session.clear()
    return redirect("/login")


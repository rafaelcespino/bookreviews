import os

from flask import Flask, session, render_template, request
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

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
    books = db.execute("SELECT * FROM books").fetchall()
    users = db.execute("SELECT * FROM users").fetchall()
    reviews = db.execute("SELECT * FROM reviews").fetchall()
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        name = request.form.get("name")

        db.execute("INSERT INTO users (username, password, name) VALUES (:username, :password, :name)",
                    {"username": username, "password": password, "name": name})
        db.commit()
        return render_template("success.html")
    
    elif request.method == "GET":
        return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        users = db.execute("SELECT * FROM users WHERE username = :username", {"username": username})
        user = users.fetchone()

        if user == None or user[1] != password:
            return render_template("invalid.html")
        else:
            return render_template("success.html")


    elif request.method == "GET":
        return render_template("login.html")
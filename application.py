import os

from flask import Flask, session, render_template, request
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from werkzeug.security import check_password_hash, generate_password_hash

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
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():

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

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        users = db.execute("SELECT * FROM users WHERE username = :username", {"username": username})
        user = users.fetchone()

        if user == None or not check_password_hash(user[2], password):
            return render_template("invalid.html", error_message="Invalid username or password", redirect="/login")
        else:
            return render_template("success.html")


    elif request.method == "GET":
        return render_template("login.html")

    
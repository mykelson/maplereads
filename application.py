import os
import requests

import json
from decimal import Decimal
from datetime import timedelta

from flask import Flask, jsonify, render_template, request, session, app
from flask_session import Session
from flask import escape, redirect, url_for
from os import urandom
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker


app = Flask(__name__)

app.debug = True
app.secret_key = urandom(24)


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

  

class fakefloat(float):
    def __init__(self, value):
        self._value = value
    def __repr__(self):
        return str(self._value)

def defaultencode(o):
    if isinstance(o, Decimal):
        # Subclass float with custom repr?
        return fakefloat(o)
    raise TypeError(repr(o) + " is not JSON serializable")

@app.before_request
def make_session_permanent():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=15)


@app.route("/")
def index():
    isbn = db.execute("SELECT isbn FROM books ORDER BY RANDOM() LIMIT 1").fetchall()
    isbn = isbn[0]
    
    for x in isbn:
        isbn = x

    book = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn": isbn}).fetchone()
    # Request book details from Google Books 
    googleRes = requests.get("https://www.googleapis.com/books/v1/volumes",
                                 params={"q": isbn})

    if googleRes.status_code != 200:
        raise Exception("ERROR: API request unsuccessful.")
    
    data0 = googleRes.json()
    book1 = data0["items"][0]["volumeInfo"]

    book_description = book1["description"]
    image = book1["imageLinks"]["thumbnail"]

    return render_template("index0.htm", book=book, book_description=book_description, image=image)


@app.route("/sign_up/<int:value>")
def sign_up(value):
    """ Take users to either the login page or sign up page """

    if value == 1:
        return render_template("login.htm")
    elif value == 2:
        return render_template("signup.htm")
    


@app.route("/register", methods=["POST"] )
def register():
    """ Register users. """

    #Get information.
    name = request.form.get("name")
    username = request.form.get("username")
    email = request.form.get("email")
    password = request.form.get("password")
    
    #Ensure that the users information sent aren't empty.
    if name == "":
        return render_template("error.htm", message="Please fill all the fields")
    elif username == "":
        return render_template("error.htm", message="Please fill all the fields")
    elif email == "":
        return render_template("error.htm", message="Please fill all the fields")
    elif password == "":
        return render_template("error.htm", message="Please fill all the fields")
        

    #Make sure there is no previous user with the same username and email.
    if db.execute("SELECT * FROM users WHERE username = :username", {"username": username}).rowcount >= 1:
        return render_template("error.htm", message="Username is already taken.")
    elif db.execute("SELECT * FROM users WHERE email = :email", {"email": email}).rowcount >= 1:
        return render_template("error.htm", message="This email has been registered to another account.")
    else:
        db.execute("INSERT INTO users (name, email, password, username) VALUES (lower(:name), lower(:email), crypt(:password, gen_salt('bf', 8)), lower(:username))", {"name": name, "username": username, "email": email, "password": password})
        db.commit()

    if request.method == 'POST':
        session['username'] = request.form['username']
        session['id'] = db.execute("SELECT id FROM users WHERE username = :username AND password = crypt(:password, password)", {"username": username, "password": password}).fetchone()
        return redirect(url_for('home'))


@app.route("/login", methods=["POST"])
def login():
    """ Log users in """

    #Get information
    username = request.form.get("username")
    password = request.form.get("password")

    if username == "":
        return render_template("error.htm", message="Please fill all the fields")
    elif password == "":
        return render_template("error.htm", message="Please fill all the fields")
    
    #Make user details are correct.
    if db.execute("SELECT * FROM users WHERE username = lower(:username)", {"username": username}).rowcount == 0:
        return render_template("error.htm", message="Invalid username.")

    user = db.execute("SELECT *FROM users WHERE username = lower(:username) AND password = crypt(:password, password)", {"username": username, "password": password}).fetchone()
    
    if user is None:
        return render_template("error.htm", message="Invalid username and password.")


    if request.method == 'POST':
        session['username'] = request.form['username']
        session['id'] = db.execute("SELECT id FROM users WHERE username = :username AND password = crypt(:password, password)", {"username": username, "password": password}).fetchone()
        return redirect(url_for('home'))


@app.route('/home', methods=['GET', 'POST'])
def home():
    #Make sure user is logged in.
    if 'username' not in session:
        return render_template("login_error.htm", message="You are not signed in!")
    else:
        username = escape(session['username'])

    return render_template("home.htm", username=username)

@app.route('/sign_out')
def sign_out():
    """ Log users out """
    session.pop('username')
    return redirect(url_for('index'))


@app.route("/search", methods=['GET', 'POST'])
def search():
    """" Searches the database for books """

    #Make sure user is logged in.
    if 'username' not in session:
        return render_template("login_error.htm", message="You are not signed in!")

    #Get search query.
    q = request.form.get("q")
    cate = request.form.get("category")

    s = "%" + q.split(" ")[0] + "%"

    if q == "":
        return render_template("error.htm", message="Please fill all fields")
    
    if cate == "title":
        results = db.execute('SELECT * FROM books WHERE title ILIKE :s', {"s": s}).fetchall() 

        return render_template("results0.htm", results=results)   
    elif cate == "author":
        results = db.execute('SELECT * FROM books WHERE author ILIKE :s', {"s": s}).fetchall() 

        return render_template("results0.htm", results=results)
    elif cate == "year":
        results = db.execute('SELECT * FROM books WHERE year = :q', {"q": q}).fetchall() 

        return render_template("results0.htm", results=results)
    elif cate == "isbn":
        results = db.execute('SELECT * FROM books WHERE title ILIKE :s', {"s": s}).fetchall() 

        return render_template("results0.htm", results=results)
            
    results = db.execute('SELECT * FROM books WHERE isbn ILIKE :s OR title ILIKE :s OR author ILIKE :s', {"s": s}).fetchall()    

    return render_template("results0.htm", results=results)


@app.route("/book/<string:isbn>")
def book(isbn):
    """ Book Details """

    #Make sure user is logged in.
    if 'username' not in session:
        return render_template("login_error.htm", message="You are not signed in!")

    #Make sure book exists.
    book = db.execute('SELECT * FROM books WHERE isbn = :isbn', {"isbn": isbn}).fetchone()

    if book is None:
        return render_template("error.htm", message= "No Such Book!!!") 

    reviews = db.execute("SELECT * FROM reviews WHERE isbn = :isbn", {"isbn": isbn}).fetchall()
    ratings = db.execute("SELECT AVG(rating) FROM reviews WHERE isbn = :isbn", {"isbn": isbn}).fetchall()
    
    # Request book details from Google Books 
    googleRes = requests.get("https://www.googleapis.com/books/v1/volumes",
                                 params={"q": isbn})

    if googleRes.status_code != 200:
        raise Exception("ERROR: API request unsuccessful.")
    
    data0 = googleRes.json()
    book1 = data0["items"][0]["volumeInfo"]

    publisher = book1["publisher"]
    book_description = book1["description"]
    image = book1["imageLinks"]["thumbnail"]

    # Request Goodreads' reviews
    res = requests.get("https://www.goodreads.com/book/review_counts.json",
                        params={"key": "Hl9uw740Ex3dG9VaX8L2CQ", "isbns": isbn})
    
    if res.status_code != 200:
        raise Exception("ERROR: API request unsuccessful.")

    data = res.json()
    goodreads_average_rating = data["books"][0]["average_rating"]
    goodreads_total_ratings = data["books"][0]["work_ratings_count"]

    return render_template("book0.htm", image=image, book_description=book_description, publisher=publisher, average_rating=ratings, goodreads_average_rating=goodreads_average_rating, goodreads_total_ratings=goodreads_total_ratings, reviews=reviews, book=book)


@app.route("/book_review/<string:isbn>", methods=["POST"])
def book_review(isbn):
    """ Save users reviews on a particular book """

    #Make sure user is logged in.
    if 'username' not in session:
        return render_template("login_error.htm", message="You are not signed in!")


    #Get user info
    username = escape(session['username'])

    #Get user review
    opinion = request.form.get("opinion")
    rating = int(request.form.get("rate"))

    #Make sure user has not previously reviewed this book.
    if db.execute("SELECT * FROM reviews WHERE username=:username AND isbn=:isbn", {"username": username, "isbn": isbn}).rowcount > 0 :
        return render_template("error.htm", message="You have previously reviewed this book")
    else:
        db.execute("INSERT INTO reviews(username, isbn, rating, opinion) VALUES (:username, :isbn, :rating, :opinion)", {"username": username, "isbn": isbn, "rating": rating, "opinion": opinion})
        db.commit()
    
    return redirect(url_for('home'))


@app.route("/api/<string:isbn>", methods=["GET"])
def book_api(isbn):
    """ Return details about a book """

    #Make sure book exists.
    book = db.execute("SELECT * FROM books WHERE isbn=:isbn", {"isbn": isbn}).fetchone()
    if book is None:
        return jsonify({"error": "Invalid Book ISBN"}), 404

    #Get the reviews of the book.
    count = db.execute("SELECT COUNT(*) FROM reviews WHERE isbn=:isbn", {"isbn": isbn}).fetchall()
    average_rating = db.execute("SELECT round(avg(rating), 2) FROM reviews WHERE isbn=:isbn", {"isbn": isbn}).fetchall()

    return json.dumps({
        "title": book.title,
        "author": book.author,
        "year": book.year,
        "isbn": book.isbn,
        "review_count": [dict(row) for row in count],
        "average_rating": [dict(row) for row in average_rating]
    }, default=defaultencode)
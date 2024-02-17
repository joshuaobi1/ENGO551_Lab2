import os
from flask import Flask, session, request, render_template, redirect, url_for, jsonify, flash
from flask_session import Session
from sqlalchemy import create_engine, text
from sqlalchemy.orm import scoped_session, sessionmaker
from werkzeug.security import generate_password_hash, check_password_hash
import requests

app = Flask(__name__)

# Setup the Flask session configuration
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Setup database connection
os.environ["DATABASE_URL"] = 'postgresql://postgres:tGreyjoy789?@localhost/ENGO551Lab1'
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///mydatabase.db")
engine = create_engine(app.config["SQLALCHEMY_DATABASE_URI"])
db = scoped_session(sessionmaker(bind=engine))



@app.route("/")
def index():
    """Landing page that offers options to register or log in."""
    return render_template("index.html")


@app.route("/home")
def home():
    """Home page after login, showing options to search for books or logout."""
    if "user_id" not in session:
        # Redirect to login if user is not in session
        flash("Please log in to continue.")
        return redirect(url_for("login"))
    return render_template("home.html")



@app.route("/register", methods=["GET", "POST"])
def register():
    """Allow users to register an account."""
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        # Check if username already exists
        if db.execute(text("SELECT * FROM users WHERE username = :username"), {"username": username}).rowcount > 0:
            flash("Username already exists.")
            return redirect(url_for("register"))

        # Hash the password and insert new user into the database
        hashed_password = generate_password_hash(password)
        db.execute(text("INSERT INTO users (username, password) VALUES (:username, :password)"), {"username": username, "password": hashed_password})
        db.commit()

        flash("Registration successful! Please log in.")
        return redirect(url_for("login"))

    return render_template("register.html")



@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        # Execute the query
        result = db.execute(text("SELECT * FROM users WHERE username = :username"), {"username": username})
        user = result.fetchone()

        # Properly convert the user row to a dictionary
        if user:
            # Use the _asdict() method if available (SQLAlchemy 1.4+)
            user_dict = user._asdict() if hasattr(user, '_asdict') else dict(user)
        else:
            user_dict = None

        if user_dict and check_password_hash(user_dict["password"], password):
            session["user_id"] = user_dict["id"]
            flash("Login successful!")
            return redirect(url_for("home"))
        else:
            flash("Invalid username or password.")
    return render_template("login.html")



@app.route("/logout")
def logout():
    """Log out users by clearing the session."""
    session.clear()
    flash("You have been logged out.")
    return redirect(url_for("index"))



@app.route("/search", methods=["GET", "POST"])
def search():
    """Provide a form for users to search for books."""
    if "user_id" not in session:
        flash("Please log in to search for books.")
        return redirect(url_for("login"))

    if request.method == "POST":
        query = "%" + request.form.get("query") + "%"
        books = db.execute(text("SELECT * FROM books WHERE isbn ILIKE :query OR title ILIKE :query OR author ILIKE :query"), {"query": query}).fetchall()
        return render_template("search_results.html", books=books)

    return render_template("search.html")



@app.route("/book/<isbn>", methods=["GET", "POST"])
def book_page(isbn):
    if "user_id" not in session:
        flash("Please log in to view book details and submit reviews.")
        return redirect(url_for("login"))

    book = db.execute(text("SELECT * FROM books WHERE isbn = :isbn"), {"isbn": isbn}).fetchone()
    if not book:
        flash("Book not found.")
        return redirect(url_for("search"))

    # Fetch reviews from database
    reviews = db.execute(text("""
        SELECT reviews.rating, reviews.review, users.username 
        FROM reviews 
        JOIN users ON reviews.user_id = users.id 
        WHERE book_isbn = :isbn
    """), {"isbn": isbn}).fetchall()

    if request.method == "POST":
        user_id = session["user_id"]
        
        # Check if the user already submitted a review for this book
        existing_review = db.execute(text("SELECT * FROM reviews WHERE user_id = :user_id AND book_isbn = :isbn"),
                                     {"user_id": user_id, "isbn": isbn}).fetchone()

        if existing_review:
            flash("You have already submitted a review for this book.")
            return redirect(url_for("book_page", isbn=isbn))

        review_content = request.form.get("review")
        rating = request.form.get("rating")

        # Insert the new review into the database
        db.execute(text("INSERT INTO reviews (user_id, book_isbn, review, rating) VALUES (:user_id, :isbn, :review, :rating)"),
                   {"user_id": user_id, "isbn": isbn, "review": review_content, "rating": rating})
        db.commit()

        flash("Thank you for submitting your review!")
        return redirect(url_for("book_page", isbn=isbn))

    # Google Books API call
    res = requests.get("https://www.googleapis.com/books/v1/volumes", params={"q": f"isbn:{isbn}"})
    google_books_data = None
    if res.status_code == 200:
        data = res.json()
        if data['totalItems'] > 0:
            google_books_data = data['items'][0]['volumeInfo']
        else:
            flash("No external review data found for this book.")

    return render_template("book_page.html", book=book, reviews=reviews, google_books_data=google_books_data)


app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

@app.route("/api/<isbn>", methods=["GET"])
def api_isbn(isbn):
    
    print(f"Accessing API for ISBN: {isbn}")
    
    # Query the database for the book with the provided ISBN
    book = db.execute(text("SELECT * FROM books WHERE isbn = :isbn"), {"isbn": isbn}).fetchone()
    
    if not book:
        return jsonify({"error": "Book not found"}), 404

    # Initialize variables
    isbn_13, average_rating, ratings_count = None, None, None

    # Make a request to the Google Books API
    try:
        res = requests.get("https://www.googleapis.com/books/v1/volumes", params={"q": f"isbn:{isbn}"})
        if res.status_code == 200:
            data = res.json()
            if data['totalItems'] > 0:
                volume_info = data['items'][0]['volumeInfo']
                
                # Extract ISBN-13
                for identifier in volume_info.get("industryIdentifiers", []):
                    if identifier["type"] == "ISBN_13":
                        isbn_13 = identifier["identifier"]
                
                # Extract averageRating and ratingsCount
                average_rating = volume_info.get("averageRating")
                ratings_count = volume_info.get("ratingsCount")
    except Exception as e:
        print(f"Error fetching data from Google Books API: {e}")

    # Construct the JSON response
    api_response = {
        "title": book.title,
        "author": book.author,
        "publishedDate": book.year,  # Assuming 'year' corresponds to 'publishedDate'
        "ISBN_10": isbn,  # The ISBN used in the query
        "ISBN_13": isbn_13,  # Extracted from Google Books API or None
        "reviewCount": ratings_count,  # Extracted from Google Books API or None
        "averageRating": average_rating  # Extracted from Google Books API or None
    }

    return jsonify(api_response)

if __name__ == "__main__":
    app.run(debug=True)




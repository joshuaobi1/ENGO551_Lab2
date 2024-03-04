# ENGO551_Lab2

Project Overview

This lab assignment focuses on developing a Flask-based web application that allows users to search for books, leave reviews, and retrieve book information through a RESTful API. The application interfaces with an external book database API to fetch book details and user reviews, offering a comprehensive platform for book enthusiasts.


Project Structure

application.py: The main Flask application file handling routes, API requests, and integration with the database for user authentication, book searches, and review submissions.

import.py: A separate script for importing book data from a CSV file into the PostgreSQL database.

templates/: This directory contains directory contains HTML files for the application's frontend. These include files for rendering the website's various pages, including login, registration, book search, book details, and API documentation.

base.html: The base template that includes the website's layout, navigation bar, and the structure for flash messages. Other templates extend this base.

index.html: The landing page template, offering options to log in or register.

login.html: The login page template.

register.html: The registration page template.

home.html: The home page template displayed after a user logs in.

search.html: The template for searching books.

search_results.html: Displays search results.

book_page.html: Displays book details and allows users to submit reviews.

requirements.txt: A list of Python package dependencies required to run the application.


Additional Information

The project uses PostgreSQL for the database back-end.

User passwords are hashed for security using Werkzeug's generate_password_hash and check_password_hash.

SQLAlchemy is used for database interaction.

Flash messages are used to provide feedback to the user.

API Integration: The application uses a third-party book API to fetch detailed information about books, including ISBNs, titles, authors, and publication years.

User Reviews: Registered users can submit reviews for books, and these reviews are displayed on the book detail pages.

API Access: The application provides a custom API endpoint (/api/<isbn>) that allows users to retrieve JSON-formatted book information by ISBN.




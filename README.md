# ENGO551_Lab2

Project Overview

This lab assignment for ENGO551 focuses on developing a Flask-based web application that allows users to search for books, leave reviews, and retrieve book information through a RESTful API. The application interfaces with an external book database API to fetch book details and user reviews, offering a comprehensive platform for book enthusiasts.


Project Structure

application.py: The main Flask application file handling routes, API requests, and integration with the database for user authentication, book searches, and review submissions.

templates/: This directory contains HTML files for rendering the website's various pages, including login, registration, book search, book details, and API documentation.

base.html: The base template that includes the website's layout and navigation bar.

index.html: The homepage template, providing links to login and register.

login.html: The login page template for user authentication.

register.html: The registration page template for new users.

search.html: The book search page template.

book_page.html: The book details page template, displaying book information and user reviews.

requirements.txt: A list of Python package dependencies required to run the application.


Additional Information

API Integration: The application uses a third-party book API to fetch detailed information about books, including ISBNs, titles, authors, and publication years.

User Reviews: Registered users can submit reviews for books, and these reviews are displayed on the book detail pages.

API Access: The application provides a custom API endpoint (/api/<isbn>) that allows users to retrieve JSON-formatted book information by ISBN.

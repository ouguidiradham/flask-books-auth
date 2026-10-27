# Flask Books API with JWT Auth

A REST API built with Python Flask, SQLite, and JWT authentication.
**Live API:** https://adhamouguidir.pythonanywhere.com

## Features
- User registration and login
- JWT protected routes
- Books CRUD operations

## Routes
- POST /register — create a user
- POST /login — login, returns token
- GET /books — get all books (public)
- POST /books — add a book (protected)
- DELETE /books/<title> — delete a book (protected)

## How to run
pip install flask flask-jwt-extended
python app.py

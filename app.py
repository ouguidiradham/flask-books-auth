import os
from dotenv import load_dotenv
load_dotenv()
import sqlite3
from flask import Flask, jsonify, request
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY", "secretkey")
jwt = JWTManager(app)

conn = sqlite3.connect("/Users/eaglefly/sqlite/books_auth.db")
cursor = conn.cursor()
cursor.execute("""CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT)""")
cursor.execute("""CREATE TABLE IF NOT EXISTS books (title TEXT PRIMARY KEY, author TEXT, pages INTEGER)""")
conn.commit()
conn.close()

@app.route("/register", methods=["POST"])
def register():
    conn = sqlite3.connect("/Users/eaglefly/sqlite/books_auth.db")
    data = request.get_json(silent=True)

    if not data:
        return jsonify({"Error":"no data provided"}), 400

    if "username" not in data:
        return jsonify({"Error":"username not provided"}), 400

    if "password" not in data:
        return jsonify({"Error":"password not provided"}), 400

    cursor = conn.cursor()
    hashed = generate_password_hash(data['password'])
    cursor.execute("INSERT INTO users (username, password) VALUES (?,?)", (data['username'],hashed))
    conn.commit()
    conn.close()

    return jsonify({"Message": f"{data['username']} added successfully "}), 201


@app.route("/login", methods=["POST"])
def login():
    conn = sqlite3.connect("/Users/eaglefly/sqlite/books_auth.db")
    data = request.get_json(silent=True)

    if not data:
        return jsonify({"Error":"no data provided"}), 400

    if "username" not in data:
        return jsonify({"Error":"username not provided"}), 400

    if "password" not in data:
        return jsonify({"Error":"password not provided"}), 400

    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (data['username'],))
    user = cursor.fetchone()

    if not user:
        conn.close()
        return jsonify({"Error":"no username found"}), 404

    if not check_password_hash(user[1], data['password']):
        conn.close()
        return jsonify({"Error":"password is wrong"}), 401

    token = create_access_token(identity=data['username'])
    conn.close()
    return jsonify({"token":f"{token}"})

@app.route("/books")
def get_book():
    conn = sqlite3.connect("/Users/eaglefly/sqlite/books_auth.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM books")
    row = cursor.fetchall()
    books = [{"title": x[0], "author": x[1], "pages": x[2]} for x in row]
    conn.close()

    return jsonify(books)

@app.route("/books", methods=["POST"])
@jwt_required()
def add_book():
    conn = sqlite3.connect("/Users/eaglefly/sqlite/books_auth.db")
    data = request.get_json(silent=True)

    if not data:
        return jsonify({"Error":"no data provided"}), 400

    if "title" not in data:
        return jsonify({"Error":"title not provided"}), 400

    if "author" not in data:
        return jsonify({"Error":"author not provided"}), 400

    if "pages" not in data:
        return jsonify({"Error":"pages not provided"}), 400

    cursor = conn.cursor()
    cursor.execute("INSERT INTO books (title, author, pages) VALUES (?, ?,?)", (data['title'], data['author'], data['pages']))
    conn.commit()
    conn.close()

    return jsonify({"Message": f"{data['title']} added successfully"}), 201


@app.route("/books/<title>", methods=["DELETE"])
@jwt_required()
def delete_book(title):
    conn = sqlite3.connect("/Users/eaglefly/sqlite/books_auth.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM books")
    before = len(cursor.fetchall())

    cursor.execute("DELETE FROM books WHERE title = ?", (title,))

    cursor.execute("SELECT * FROM books")
    after = len(cursor.fetchall())

    if before == after:
        conn.close()
        return jsonify({"Error": "no title found"}), 404

    conn.commit()
    conn.close()
    return jsonify({"Message": f"{title} deleted successfully"}), 201

if __name__ == "__main__":
    app.run(debug=True)

from db_files.database import db_path
from werkzeug.security import generate_password_hash

import sqlite3

def add_user(username, password):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    password_hash = generate_password_hash(password)  # Updated hashing method
    try:
        cursor.execute('INSERT INTO users (username, password_hash) VALUES (?, ?)', (username, password_hash))
        conn.commit()
        print(f"User '{username}' was added to the database.")
    except sqlite3.IntegrityError:
        print("Username already exists.")
    conn.close()

def get_user_by_username(username):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    # print("PRINTING FROM DB")
    # print(user)
    conn.close()
    return user

def get_user_by_id(id):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (id,))
    user = cursor.fetchone()
    # print("PRINTING FROM DB")
    # print(user)
    conn.close()
    return user

def remove_user_by_username(username):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('DELETE FROM users WHERE username = ?', (username,))
    
    conn.commit()
    conn.close()
    print(f"User '{username}' was deleted from the database.")

def get_all_users():
    # Replace this with actual database fetching logic
    return [
        {'id': 1, 'username': 'test_user', 'password': 'hashed_password_here'},
        {'id': 2, 'username': 'another_user', 'password': 'hashed_password_here'},
    ]
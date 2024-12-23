import sqlite3
from flask_login import UserMixin
from werkzeug.security import generate_password_hash



db_path = './data/planeswalker.db'

def database_setup():
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(
        '''
            CREATE TABLE IF NOT EXISTS planeswalkers (
            name TEXT PRIMARY KEY,
            collected BOOLEAN,
            set_code TEXT,
            collected_set TEXT,
            print_order INT,
            image_url TEXT

            )
        '''
                   )
    conn.commit()
    conn.close()

def planeswalker_create(name, collected, print_order, set_code, collected_set):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('''
        INSERT OR REPLACE INTO planeswalkers (name, collected, print_order,set_code,collected_set)
        VALUES (?, ?, ?, ?, ?)
    ''', (name, collected, print_order, set_code, collected_set))
    
    conn.commit()
    conn.close()
    print(f"Planeswalker '{name}' added with collected status: {collected}")

def planeswalker_read_all():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('SELECT name, collected, set_code, collected_set, image_url FROM planeswalkers')
    results = cursor.fetchall()

    conn.close()
    return results

def planeswalker_read_status(collected):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM planeswalkers WHERE collected = ?', (collected,))
    results = cursor.fetchall()

    conn.close()
    return results

def planeswalker_update(name, collected, collected_set):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('''
        UPDATE planeswalkers
        SET collected = ?, collected_set = ?
        WHERE name = ?
    ''', (collected, collected_set, name))
    
    conn.commit()
    conn.close()
    print(f"Planeswalker '{name}' updated to collected status: {collected}")

def plansewalker_delete(name):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('DELETE FROM planeswalkers WHERE name = ?', (name,))
    
    conn.commit()
    conn.close()
    print(f"Planeswalker '{name}' deleted from the database.")

def planeswalker_delete_all():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('DELETE FROM planeswalkers')
    
    conn.commit()
    conn.close()
    print("All planeswalkers deleted from the database.")

# Adding user logins for the editing
def create_users_table():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def add_user(username, password):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    password_hash = generate_password_hash(password).decode('utf-8')  # Updated hashing method
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
    print("PRINTING FROM DB")
    print(user)
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
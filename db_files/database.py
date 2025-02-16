import sqlite3
from werkzeug.security import generate_password_hash

db_path = './data/collection.db'

def database_setup():
    # Create tables
    create_planeswalker_table()
    create_users_table()
    create_outlaws_table()
    create_murders_table()
    # Indices and Views
    create_indices()
    #Cleanup and Aux functions
    run_table_cleanup()


def create_planeswalker_table():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
            CREATE TABLE IF NOT EXISTS planeswalkers (
            name TEXT PRIMARY KEY,
            collected BOOLEAN DEFAULT 0,
            set_code TEXT,
            collected_set TEXT DEFAULT '',
            collector_number INT DEFAULT 0,
            print_order INT,
            image_url TEXT
            )
    
        '''
    )

    conn.commit()
    conn.close()

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

def create_indices():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_planeswalkers_name ON planeswalkers (name)
    ''')
    conn.commit()
    conn.close()

def run_table_cleanup():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
    UPDATE planeswalkers
    SET collector_number = ''
    WHERE collector_number = 'None';                   
''')
    cursor.execute('''
    UPDATE outlaws
    SET collector_number = ''
    WHERE collector_number = 'None';                   
''')
    cursor.execute('''
    UPDATE planeswalkers
    SET image_url = Null
    WHERE image_url = '';                   
''')
    cursor.execute('''
    UPDATE outlaws
    SET image_url = Null
    WHERE image_url = '';                   
''')
    cursor.execute('''
    UPDATE murders
    SET image_url = Null
    WHERE image_url = '';                   
''')
    cursor.execute('''
    UPDATE murders
    SET collector_number = ''
    WHERE collector_number = 'None';                   
''')
    cursor.execute(
        '''
    DELETE FROM outlaws
    WHERE name = 'Forest'
    OR
    name = 'Plains'
    OR
    name = 'Mountain'
    OR
    name = 'Swamp'
    OR
    name = 'Island'
'''
    )
    conn.commit()
    conn.close()

def create_outlaws_table():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS murders (
            name TEXT PRIMARY KEY,
            collected INT DEFAULT 0,
            set_code TEXT,
            collector_number INT,
            image_url TEXT
        )
    ''')

def create_murders_table():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS murders (
            name TEXT PRIMARY KEY,
            collected INT DEFAULT 0,
            set_code TEXT,
            collector_number INT,
            image_url TEXT
        )
    ''')

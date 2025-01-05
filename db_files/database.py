import sqlite3
from flask import current_app
from werkzeug.security import generate_password_hash

DB_PATH = './data/collection.db'

def database_setup():
    # Create tables
    create_planeswalker_table()
    create_users_table()
    create_outlaws_table()
    create_murders_table()
    create_score_table()
    create_trades_table()
    # Indices and Views
    create_indices()
    #Cleanup and Aux functions
    run_table_cleanup()

# ************* #
# CREATE TABLES #
# ************* #
def create_planeswalker_table():
    DB_PATH = current_app.config['DB_PATH']
    conn = sqlite3.connect(DB_PATH)

    cursor = conn.cursor()
    cursor.execute('''
            CREATE TABLE IF NOT EXISTS planeswalkers (
            name TEXT PRIMARY KEY,
            collected BOOLEAN DEFAULT 0,
            set_code TEXT,
            collected_set TEXT DEFAULT '',
            collector_number INT DEFAULT 0,
            print_order INT,
            image_url TEXT,
            price SMALLMONEY
            )
    
        '''
    )

    conn.commit()
    conn.close()

def create_murders_table():
    DB_PATH = current_app.config['DB_PATH']
    conn = sqlite3.connect(DB_PATH)

    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS murders (
            name TEXT PRIMARY KEY,
            collected INT DEFAULT 0,
            set_code TEXT,
            collector_number INT,
            image_url TEXT,
            rarity TEXT,
            price SMALLMONEY
        )
    ''')

def create_outlaws_table():
    DB_PATH = current_app.config['DB_PATH']
    conn = sqlite3.connect(DB_PATH)

    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS outlaws (
            name TEXT PRIMARY KEY,
            collected INT DEFAULT 0,
            set_code TEXT,
            collector_number INT,
            image_url TEXT,
            rarity TEXT,
            price SMALLMONEY
        )
    ''')

def create_score_table():
    DB_PATH = current_app.config['DB_PATH']
    conn = sqlite3.connect(DB_PATH)

    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS score (
            name TEXT PRIMARY KEY,
            collected INT DEFAULT 0,
            set_code TEXT,
            collector_number INT,
            image_url TEXT,
            rarity TEXT,
            price SMALLMONEY
        )
    ''')

def create_users_table():
    DB_PATH = current_app.config['DB_PATH']
    conn = sqlite3.connect(DB_PATH)

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

def create_trades_table():
    DB_PATH = current_app.config['DB_PATH']
    conn = sqlite3.connect(DB_PATH)

    cursor = conn.cursor()
    cursor.execute('''
            CREATE TABLE IF NOT EXISTS trades (
            name TEXT PRIMARY KEY,
            collected INT DEFAULT 0,
            collected_set TEXT DEFAULT '',
            collector_number INT DEFAULT 0,
            print_order INT,
            image_url TEXT,
            price SMALLMONEY
            )
    
        '''
    )

    conn.commit()
    conn.close()

# ***************** #
# INDICES AND VIEWS #
# ***************** #

def create_indices():
    DB_PATH = current_app.config['DB_PATH']
    conn = sqlite3.connect(DB_PATH)

    cursor = conn.cursor()
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_planeswalkers_name ON planeswalkers (name)
    ''')
    conn.commit()
    conn.close()

# *************** #
# CLEANUP AND AUX #
# *************** #
def run_table_cleanup():
    DB_PATH = current_app.config['DB_PATH']
    conn = sqlite3.connect(DB_PATH)

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

    cursor.execute('''
    UPDATE score
    SET image_url = Null
    WHERE image_url = '';                   
''')
    conn.commit()
    conn.close()

def drop_table(table_name):
    DB_PATH = current_app.config['DB_PATH']
    conn = sqlite3.connect(DB_PATH)

    cursor = conn.cursor()

    try:
        # Dynamically format the query to include the table name
        cursor.execute(f"DROP TABLE IF EXISTS {table_name};")
        conn.commit()
        print(f"Deleted table '{table_name}' from the database.")
    except sqlite3.Error as e:
        print(f"Error while dropping table '{table_name}': {e}")
    finally:
        conn.close()

def alter_tables(table_name,column,datatype):
    DB_PATH = current_app.config['DB_PATH']
    conn = sqlite3.connect(DB_PATH)

    cursor = conn.cursor()

    try:
        # Dynamically format the query to include the table name
        cursor.execute(f'''ALTER TABLE {table_name}
                       ADD {column} {datatype}
                       ''')
        conn.commit()
        print(f"Added '{column}' with datatype '{datatype}' to table '{table_name}' in the database.")
    except sqlite3.Error as e:
        print(f"Error adding '{column}' to table '{table_name}': {e}")
    finally:
        conn.close()
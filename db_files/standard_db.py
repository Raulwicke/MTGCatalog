from db_files.database import db_path
import csv
import sqlite3
import requests

# **************** #
# IMPORT FUNCTIONS #
# **************** #

def import_outlaws(csv_path):  
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    with open(csv_path, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            cursor.execute('''
                INSERT OR REPLACE INTO outlaws (name, collected, set_code, collector_number, image_url)
                VALUES (?, ?, ?, ?, ?)
            ''',(row['name'], row['collected'], row['set'], row['collector_number'], ''))
            print(f"Updated {row['name']} in the database.")

    conn.commit()
    conn.close()

def import_murders(csv_path):  
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    with open(csv_path, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            cursor.execute('''
                INSERT OR REPLACE INTO murders (name, collected, set_code, collector_number, image_url)
                VALUES (?, ?, ?, ?, ?)
            ''', (row['name'], row['collected'], row['set'], row['collector_number'], ''))
            print(f"Updated {row['name']} in the database.")

    
    conn.commit()
    conn.close()

def import_score(csv_path):  
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    with open(csv_path, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            cursor.execute('''
                INSERT OR REPLACE INTO score (name, collected, set_code, collector_number, image_url)
                VALUES (?, ?, ?, ?, ?)
            ''', (row['name'], 0, row['set'], row['collector_number'], ''))
            print(f"Updated {row['name']} in the database.")

    
    conn.commit()
    conn.close()
# ***************** #
# GENERAL FUNCTIONS #
# ***************** #

# Update rarity for a single card
def update_card_rarity(name, set_code, table_name):
    try:
        # Fetch card details from Scryfall
        url = f"https://api.scryfall.com/cards/named?fuzzy={name}&set={set_code}"
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        
        card_data = response.json()
        rarity = card_data.get("rarity")
        
        if not rarity:
            print(f"Rarity not found for {name} ({set_code})")
            return
        
        # Connect to the database
        conn = sqlite3.connect(db_path)  # Use the saved db_path variable
        cursor = conn.cursor()
        
        # Update the rarity in the database
        query = f'''
            UPDATE {table_name}
            SET rarity = ?
            WHERE name = ? AND set_code = ?
        '''
        cursor.execute(query, (rarity, name, set_code))
        conn.commit()
        print(f"Updated rarity for {name} ({set_code}) to {rarity}")
    
    except requests.exceptions.RequestException as e:
        print(f"Error fetching rarity for {name} ({set_code}): {e}")
    except sqlite3.Error as db_error:
        print(f"Database error: {db_error}")
    finally:
        conn.close()

# Batch update rarity for all cards in a specified table
def batch_update_card_rarities(table_name):
    try:
        # Connect to the database
        conn = sqlite3.connect(db_path)  # Use the saved db_path variable
        cursor = conn.cursor()
        
        # Retrieve all cards from the specified table
        query = f"SELECT name, set_code FROM {table_name}"
        cursor.execute(query)
        cards = cursor.fetchall()
        
        for name, set_code in cards:
            update_card_rarity(name, set_code, table_name)  # Call the update function for each card
    
    except sqlite3.Error as db_error:
        print(f"Database error: {db_error}")
    finally:
        conn.close()

# ************** #
# READ FUNCTIONS #
# ************** #

def outlaws_read_all():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM outlaws ORDER BY collector_number')
    outlaws_data = cursor.fetchall()
    conn.close()

    return outlaws_data

def murders_read_all():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM murders ORDER BY collector_number')
    outlaws_data = cursor.fetchall()
    conn.close()

    return outlaws_data

def score_read_all():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM score ORDER BY collector_number')
    score_data = cursor.fetchall()
    conn.close()

    return score_data
# **************** #
# UPDATE FUNCTIONS #
# **************** #

def update_murders_card(collector_number, collected):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE murders
        SET collected = ?
        WHERE collector_number = ?
    """, (collected, collector_number))
    conn.commit()
    conn.close()

def update_outlaw_card(collector_number, collected):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE outlaws
        SET collected = ?
        WHERE collector_number = ?
    """, (collected, collector_number))
    conn.commit()
    conn.close()

def update_score_card(collector_number, collected):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE score
        SET collected = ?
        WHERE collector_number = ?
    """, (collected, collector_number))
    conn.commit()
    conn.close()
# **************** #
# SEARCH FUNCTIONS #
# **************** #

def outlaws_advanced_search(name='', collected='', full_set='', rarity=''):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Base query
    query = '''
        SELECT name, collected, set_code, collector_number, image_url, rarity
        FROM outlaws
        WHERE 1=1
    '''
    params = []

    # Append conditions dynamically
    if name:
        query += ' AND name LIKE ?'
        params.append(f'%{name}%')
    if collected:
        if collected.lower() == 'true':
            query += ' AND collected > 0'
        elif collected.lower() == 'false':
            query += ' AND collected = 0'
    if full_set:
        print(full_set)
        if full_set.lower() == 'true':
            query += ' AND collected = 4'
        elif full_set.lower() == 'false':
            query += ' AND collected < 4'
    if rarity:
        query += ' AND rarity = ?'
        params.append(rarity.lower())

    query += ' ORDER BY collector_number'

    print(f"DEBUG: Executing query: {query} with params {params}")  # Debug log

    cursor.execute(query, params)
    results = cursor.fetchall()

    conn.close()
    return results

def murders_advanced_search(name='', collected='', full_set='', rarity=''):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Base query
    query = '''
        SELECT name, collected, set_code, collector_number, image_url, rarity
        FROM murders
        WHERE 1=1
    '''
    params = []

    # Append conditions dynamically
    if name:
        query += ' AND name LIKE ?'
        params.append(f'%{name}%')
    if collected:
        if collected.lower() == 'true':
            query += ' AND collected > 0'
        elif collected.lower() == 'false':
            query += ' AND collected = 0'
    if full_set:
        print(full_set)
        if full_set.lower() == 'true':
            query += ' AND collected = 4'
        elif full_set.lower() == 'false':
            query += ' AND collected < 4'
    if rarity:
        query += ' AND rarity = ?'
        params.append(rarity.lower())

    query += ' ORDER BY collector_number'

    print(f"DEBUG: Executing query: {query} with params {params}")  # Debug log

    cursor.execute(query, params)
    results = cursor.fetchall()

    conn.close()
    return results

def score_advanced_search(name='', collected='', full_set='', rarity=''):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Base query
    query = '''
        SELECT name, collected, set_code, collector_number, image_url
        FROM score
        WHERE 1=1
    '''
    params = []

    # Append conditions dynamically
    if name:
        query += ' AND name LIKE ?'
        params.append(f'%{name}%')
    if collected:
        if collected.lower() == 'true':
            query += ' AND collected > 0'
        elif collected.lower() == 'false':
            query += ' AND collected = 0'
    if full_set:
        print(full_set)
        if full_set.lower() == 'true':
            query += ' AND collected = 4'
        elif full_set.lower() == 'false':
            query += ' AND collected < 4'

    query += ' ORDER BY collector_number'

    print(f"DEBUG: Executing query: {query} with params {params}")  # Debug log

    cursor.execute(query, params)
    results = cursor.fetchall()

    conn.close()
    return results
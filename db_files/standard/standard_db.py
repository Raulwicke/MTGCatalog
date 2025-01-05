import csv
import sqlite3
import requests

from flask import current_app

# **************** #
# IMPORT FUNCTIONS #
# **************** #

def import_outlaws(csv_path):  
    DB_PATH = current_app.config['DB_PATH']
    conn = sqlite3.connect(DB_PATH)
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
    DB_PATH = current_app.config['DB_PATH']
    conn = sqlite3.connect(DB_PATH)
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
    DB_PATH = current_app.config['DB_PATH']
    conn = sqlite3.connect(DB_PATH)
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

# **************** #
# UPDATE FUNCTIONS #
# **************** #

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
        DB_PATH = current_app.config['DB_PATH']
        conn = sqlite3.connect(DB_PATH)  # Use the saved DB_PATH variable
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
        DB_PATH = current_app.config['DB_PATH']
        conn = sqlite3.connect(DB_PATH)  # Use the saved DB_PATH variable
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

# Update price for a single card
def update_card_price(name, set_code, table_name):
    try:
        # Fetch card details from Scryfall
        url = f"https://api.scryfall.com/cards/named?fuzzy={name}&set={set_code}"
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        
        card_data = response.json()
        price = card_data.get("prices").get("usd")
        
        if not price:
            print(f"Price not found for {name} ({set_code})")
            return
        
        # Connect to the database
        DB_PATH = current_app.config['DB_PATH']
        conn = sqlite3.connect(DB_PATH)  # Use the saved DB_PATH variable
        cursor = conn.cursor()
        
        # Update the rarity in the database
        query = f'''
            UPDATE {table_name}
            SET price = ?
            WHERE name = ? AND set_code = ?
        '''
        cursor.execute(query, (price, name, set_code))
        conn.commit()
        print(f"Updated price for {name} ({set_code}) to {price}")
    
    except requests.exceptions.RequestException as e:
        print(f"Error fetching price for {name} ({set_code}): {e}")
    except sqlite3.Error as db_error:
        print(f"Database error: {db_error}")
    finally:
        conn.close()

# Batch update rarity for all cards in a specified table
def batch_update_card_prices(table_name):
    try:
        # Connect to the database
        DB_PATH = current_app.config['DB_PATH']
        conn = sqlite3.connect(DB_PATH)  # Use the saved DB_PATH variable
        cursor = conn.cursor()
        
        # Retrieve all cards from the specified table
        query = f"SELECT name, set_code FROM {table_name}"
        cursor.execute(query)
        cards = cursor.fetchall()
        
        for name, set_code in cards:
            update_card_price(name, set_code, table_name)  # Call the update function for each card
    
    except sqlite3.Error as db_error:
        print(f"Database error: {db_error}")
    finally:
        conn.close()

# *************** #
# FETCH FUNCTIONS #
# *************** #

def fetch_collection_stats():
    DB_PATH = current_app.config['DB_PATH']
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Fetch total cards and collected stats
    stats = {}
    cursor.execute("SELECT COUNT(*) FROM outlaws WHERE collected > 0")
    stats['outlaws_collected'] = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM murders WHERE collected > 0")
    stats['murders_collected'] = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM planeswalkers WHERE collected > 0")
    stats['planeswalkers_collected'] = cursor.fetchone()[0]

    # Close connection
    conn.close()
    return stats

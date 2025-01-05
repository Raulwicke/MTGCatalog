import sqlite3
from flask import current_app

def outlaws_read_all():
    DB_PATH = current_app.config['DB_PATH']
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM outlaws ORDER BY collector_number')
    outlaws_data = cursor.fetchall()
    conn.close()

    return outlaws_data

def update_outlaw_card(collector_number, collected):
    DB_PATH = current_app.config['DB_PATH']
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE outlaws
        SET collected = ?
        WHERE collector_number = ?
    """, (collected, collector_number))
    conn.commit()
    conn.close()

def outlaws_advanced_search(name='', collected='', full_set='', rarity='', price = ''):
    DB_PATH = current_app.config['DB_PATH']
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Base query
    query = '''
        SELECT name, collected, set_code, collector_number, image_url, rarity, price
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
    if price:
        query += ' AND price >= ?'
        params.append(price)

    query += ' ORDER BY collector_number'

    print(f"DEBUG: Executing query: {query} with params {params}")  # Debug log

    cursor.execute(query, params)
    results = cursor.fetchall()

    conn.close()
    return results

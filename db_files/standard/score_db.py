import sqlite3
from flask import current_app

def score_read_all():
    DB_PATH = current_app.config['DB_PATH']
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM score ORDER BY collector_number')
    score_data = cursor.fetchall()
    conn.close()

    return score_data

def update_score_card(collector_number, collected):
    DB_PATH = current_app.config['DB_PATH']
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE score
        SET collected = ?
        WHERE collector_number = ?
    """, (collected, collector_number))
    conn.commit()
    conn.close()

def score_advanced_search(name='', collected='', full_set='', price = ''):

    DB_PATH = current_app.config['DB_PATH']
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Base query
    query = '''
        SELECT name, collected, set_code, collector_number, image_url, price
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
    if price:
        query += ' AND price >= ?'
        params.append(price)

    query += ' ORDER BY collector_number'

    print(f"DEBUG: Executing query: {query} with params {params}")  # Debug log

    cursor.execute(query, params)
    results = cursor.fetchall()

    conn.close()
    return results


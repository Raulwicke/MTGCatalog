from db_files.database import db_path
import sqlite3

def planeswalker_create(name, collected, print_order, set_code, collected_set, collector_number = None):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('''
        INSERT OR REPLACE INTO planeswalkers (name, collected, print_order,set_code,collected_set, collector_number)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (name, collected, print_order, set_code, collected_set, collector_number))
    
    conn.commit()
    conn.close()
    print(f"Planeswalker '{name}' added with collected status: {collected}")

def planeswalker_read_all():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('SELECT name, collected, set_code, collected_set, collector_number, image_url FROM planeswalkers')
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

def planeswalker_read_specific(name):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM planeswalkers WHERE name = ?', (name,))
    results = cursor.fetchall()

    conn.close()
    return results

def planeswalker_update(name, collected, collected_set, collector_number):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        cursor.execute('''
            UPDATE planeswalkers
            SET collected = ?,
                collected_set = COALESCE(?, collected_set),
                collector_number = COALESCE(?, collector_number)
            WHERE name = ?
        ''', (collected, collected_set, collector_number, name))
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


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

def planeswalker_search(query):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Use SQL LIKE for partial matches
    cursor.execute('''
        SELECT name, collected, set_code, collected_set, collector_number, image_url
        FROM planeswalkers
        WHERE name LIKE ? OR set_code LIKE ? OR collected_set LIKE ?
    ''', (f'%{query}%', f'%{query}%', f'%{query}%'))

    results = cursor.fetchall()
    # print(f"DEBUG: Database search results for query '{query}': {results}")  # Log query results

    conn.close()
    return results

def planeswalker_advanced_search(name='', collected='', set_code='', collector_number=''):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Base query
    query = '''
        SELECT name, collected, set_code, collected_set, collector_number, image_url
        FROM planeswalkers
        WHERE 1=1
    '''
    params = []

    # Append conditions dynamically
    if name:
        query += ' AND name LIKE ?'
        params.append(f'%{name}%')
    if collected:
        query += ' AND collected = ?'
        params.append(1 if collected.lower() == 'true' else 0)
    if set_code:
        query += ' AND set_code LIKE ?'
        params.append(f'%{set_code}%')
    if collector_number:
        query += ' AND collector_number = ?'
        params.append(collector_number)

    # print(f"DEBUG: Executing query: {query} with params {params}")  # Debug log

    cursor.execute(query, params)
    results = cursor.fetchall()

    conn.close()
    return results

def batch_planeswalker_update(planeswalker_data):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        cursor.execute("BEGIN TRANSACTION;")  # Start a transaction
        for pw_data in planeswalker_data:
            cursor.execute('''
                UPDATE planeswalkers
                SET collected = ?, collected_set = ?, collector_number = ?
                WHERE name = ?
            ''', (pw_data['collected'], pw_data['collected_set'], pw_data['collector_number'], pw_data['name']))
        conn.commit()  # Commit all changes at once
    except Exception as e:
        conn.rollback()  # Roll back on error
        raise e
    finally:
        conn.close()

def get_planeswalker_by_name(name):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('''
        SELECT name, collected, set_code, collected_set, collector_number, image_url
        FROM planeswalkers
        WHERE name = ?
    ''', (name,))
    row = cursor.fetchone()
    conn.close()

    if row:
        return {
            'name': row[0],
            'collected': bool(row[1]),
            'set_code': row[2],
            'collected_set': row[3],
            'collector_number': row[4],
            'image_url': row[5]
        }
    return None
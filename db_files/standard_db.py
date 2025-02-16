from db_files.database import db_path
import csv
import sqlite3

def import_outlaws(csv_path):  
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    with open(csv_path, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            cursor.execute('''
                INSERT OR REPLACE INTO outlaws (name, collected, set_code, collector_number, image_url)
                VALUES (?, ?, ?, ?, ?)
            ''', (row['name'], 0, row['set'], row['collector_number'], ''))
    
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

def outlaws_read_all():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM outlaws ORDER BY collector_number')
    outlaws_data = cursor.fetchall()
    conn.close()

    return outlaws_data


def import_murders(csv_path):  
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    with open(csv_path, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            cursor.execute('''
                INSERT OR REPLACE INTO murders (name, collected, set_code, collector_number, image_url)
                VALUES (?, ?, ?, ?, ?)
            ''', (row['name'], 0, row['set'], row['collector_number'], ''))
    
    conn.commit()
    conn.close()

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

def murders_read_all():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM murders ORDER BY collector_number')
    outlaws_data = cursor.fetchall()
    conn.close()

    return outlaws_data
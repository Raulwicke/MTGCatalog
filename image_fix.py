import sqlite3
import requests
import time
from db_files.database import db_path

# Fetch card image from Scryfall with support for collector numbers
def fetch_card_image_url(card_name, set_code, collector_number=None):
    """
    Fetch the image URL for a card from Scryfall.
    Handles single-faced, double-faced, meld cards, and collector numbers.
    """
    # Construct the Scryfall query URL

    if "//" in card_name:
        card_name = card_name.split(" //")[0]
  
    if collector_number:
        query_url = f"https://api.scryfall.com/cards/{set_code}/{collector_number}"
    else:
        query_url = f"https://api.scryfall.com/cards/named?fuzzy={card_name}&set={set_code}"
    
    try:
        response = requests.get(query_url)
        response.raise_for_status()
        card_data = response.json()

        # Extract image URI
        if 'card_faces' in card_data and 'image_uris' not in card_data:
            # Meld or double-faced cards with image URLs in `card_faces`
            return card_data['card_faces'][0]['image_uris']['normal']
        elif 'image_uris' in card_data:
            return card_data['image_uris']['normal']
        else:
            print(f"Warning: No image found for {card_name} ({set_code})")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error fetching image for {card_name} ({set_code}): {e}")
        return None

# Update card image URL in the database
def update_card_image_url(card_name, image_url):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        # Update both tables
        cursor.execute(
            "UPDATE planeswalkers SET image_url = ? WHERE name = ?",
            (image_url, card_name)
        )
        cursor.execute(
            "UPDATE outlaws SET image_url = ? WHERE name = ?",
            (image_url, card_name)
        )
        cursor.execute(
            "UPDATE murders SET image_url = ? WHERE name = ?",
            (image_url, card_name)
        )
        cursor.execute(
            "UPDATE score SET image_url = ? WHERE name = ?",
            (image_url, card_name)
        )
        conn.commit()
        print(f"Updated image URL for {card_name}")
    except Exception as e:
        print(f"Error updating database for {card_name}: {e}")
    finally:
        conn.close()

# Process updated images based on collector number
def process_updated_images(card_name, set_code, collector_number=None):
    try:
        # Fetch image URL
        image_url = fetch_card_image_url(card_name, set_code, collector_number)
        if image_url:
            update_card_image_url(card_name, image_url)
        else:
            print(f"Image not found for {card_name} ({set_code}, Collector Number: {collector_number})")
        time.sleep(0.1)  # Small delay to avoid overwhelming Scryfall API
    except Exception as e:
        print(f"Error processing database: {e}")

# Process all missing images in the database
def process_missing_images():
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Get all table names from the SQLite schema
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]

        total_missing_entries = 0

        for table in tables:
            # Skip tables that don't have the relevant columns
            cursor.execute(f"PRAGMA table_info({table})")
            columns = [col[1] for col in cursor.fetchall()]
            if not {"name", "set_code", "collector_number", "image_url"}.issubset(columns):
                continue

            # Fetch all entries missing image URLs from the current table
            query = f"SELECT name, set_code, collector_number FROM {table} WHERE image_url IS NULL"
            cursor.execute(query)
            missing_entries = cursor.fetchall()

            total_missing_entries += len(missing_entries)

            print(f"Table '{table}': Found {len(missing_entries)} entries missing images.")

            for card_name, set_code, collector_number in missing_entries:
                process_updated_images(card_name, set_code, collector_number)

        conn.close()
        print(f"Processing complete. Total missing entries across all tables: {total_missing_entries}")
    except Exception as e:
        print(f"Error processing database: {e}")

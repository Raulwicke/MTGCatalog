import sqlite3
import requests
import time
import database
# Replace with your actual database file path

database_path = database.db_path

# Fetch card image from Scryfall
def fetch_card_image_url(card_name, set_code):
    """
    Fetch the image URL for a card from Scryfall.
    Handles single-faced, double-faced, and meld cards.
    """
    import requests

    # Handle double-faced or split cards by using just the first name part
    if "//" in card_name:
        card_name = card_name.split(" //")[0]

    # Construct the Scryfall query URL
    query_url = f"https://api.scryfall.com/cards/search?q=!\"{card_name}\"+set:{set_code}"
    try:
        response = requests.get(query_url)
        response.raise_for_status()
        card_data = response.json()

        # Check if the card was found
        if not card_data.get('data'):
            print(f"Warning: No card found for {card_name} ({set_code})")
            return None

        # Extract card image information
        card_info = card_data['data'][0]  # Use the first result
        if 'card_faces' in card_info and 'image_uris' not in card_info:
            # Meld or double-faced cards with image URLs in `card_faces`
            return card_info['card_faces'][0]['image_uris']['normal']
        elif 'image_uris' in card_info:
            return card_info['image_uris']['normal']
        else:
            print(f"Warning: No image found for {card_name} ({set_code})")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error fetching image for {card_name} ({set_code}): {e}")
        return None


# Update card image URL in the database
def update_card_image_url(card_name, image_url):
    try:
        conn = sqlite3.connect(database_path)
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE planeswalkers SET image_url = ? WHERE name = ?",
            (image_url, card_name)
        )
        conn.commit()
        print(image_url)
        print(f"Updated image URL for {card_name}")
    except Exception as e:
        print(f"Error updating database for {card_name}: {e}")

# Main function to process database entries
def process_missing_images():
    try:
        # Connect to the database
        conn = sqlite3.connect(database_path)
        cursor = conn.cursor()

        # Fetch all planeswalkers missing image URLs
        cursor.execute("SELECT name, set_code FROM planeswalkers WHERE image_url IS NULL")
        missing_entries = cursor.fetchall()

        print(f"Found {len(missing_entries)} entries missing images.")

        for card_name, set_code in missing_entries:
            image_url = fetch_card_image_url(card_name, set_code)
            if image_url:
                update_card_image_url(conn, card_name, image_url)
            time.sleep(0.1)  # Small delay to avoid overwhelming Scryfall API

        conn.close()
        print("Processing complete.")
    except Exception as e:
        print(f"Error processing database: {e}")

def process_updated_images(card_name, collected_set):
    try:
        # Connect to the database
        conn = sqlite3.connect(database_path)
        cursor = conn.cursor()

        # Fetch all planeswalkers missing image URLs
        image_url = fetch_card_image_url(card_name, collected_set)
        print(image_url)
        if image_url:
            update_card_image_url(card_name, image_url)
        time.sleep(0.1)  # Small delay to avoid overwhelming Scryfall API

        conn.close()
        print("Processing complete.")
    except Exception as e:
        print(f"Error processing database: {e}")
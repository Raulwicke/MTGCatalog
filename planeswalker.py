import scrython as scry
import db_files.database as db
import csv
import asyncio
import db_files.database
import db_files.pw_db
import image_fix
import db_files.standard_db

# Ensure the database is set up

def add_planeswalker(name, collected, print_order, set_code, collected_set=None):
    """
    Add a planeswalker to the database, including the image URL.
    """
    try:
        # Use set_code if collected_set is not provided
        db_files.pw_db.planeswalker_create(name, collected, print_order, set_code, collected_set)
    except Exception as e:
        print(f"Error adding {name} to the database: {e}")

def update_planeswalker(name, collected, set_code, collected_set, print_order):
    """
    Update an existing planeswalker in the database.
    """
    try:
        db_files.pw_db.planeswalker_update(name, collected, set_code, collected_set, print_order)
        print(f"Updated {name} in the database.")
    except Exception as e:
        print(f"Error updating {name}: {e}")

def import_planeswalkers_from_csv(file_path):
    """
    Import planeswalkers from a CSV file and add them to the database.
    """
    try:
        with open(file_path, mode='r') as file:
            planeswalkers = csv.DictReader(file)
            print(f"Detected CSV Headers: {planeswalkers.fieldnames}")
            for row in planeswalkers:
                try:
                    name = row['Name']
                    collected = row['Collected'].strip().lower() in ('true', '1', 'yes')
                    print_order = int(row['Release Order'])
                    set_code = row['Original Printing']
                    collected_set = row.get('Collected Set')  # Safe retrieval
                    add_planeswalker(name, collected, print_order, set_code, collected_set)
                except Exception as e:
                    print(f"Error processing row {row}: {e}")
    except FileNotFoundError:
        print(f"File not found: {file_path}")
    except Exception as e:
        print(f"Error importing from CSV: {e}")

# Main execution
if __name__ == "__main__":

    # db_files.database.drop_table('outlaws')
    db.database_setup()
    # loop = asyncio.get_event_loop()
    # print(f"Loop running: {loop.is_running()}")
    
    # import_planeswalkers_from_csv('planeswalkers.csv')
    db_files.standard_db.import_outlaws('./csvs/otj.csv')
    # db_files.standard_db.import_murders('./csvs/murders_collection.csv')
    # db_files.standard_db.import_score('./csvs/big.csv')

    # db_files.standard_db.batch_update_card_rarities('score')

    # db_files.standard_db.batch_update_card_rarities('murders')

    db.run_table_cleanup()
    db_files.standard_db.batch_update_card_rarities('outlaws')
    image_fix.process_missing_images()

    None
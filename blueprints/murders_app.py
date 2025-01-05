import sqlite3,csv, io
from flask import current_app

from flask import Blueprint, render_template, request, redirect, url_for, flash, Response
from flask_login import login_required
from db_files.standard.murders_db import (
    murders_read_all,
    murders_advanced_search,
    update_murders_card
    )
from utils.image_fix import process_updated_images

# Blueprint Definition
murders_bp = Blueprint('murders', __name__, template_folder='templates', static_folder='static')

@murders_bp.route('/collections/mkm', methods=['GET'])
def murders():
    murders = murders_read_all()
    
    name = request.args.get('name', '').strip()
    collected = request.args.get('collected', '').strip()
    set_code = request.args.get('full_set', '').strip()
    rarity = request.args.get('rarity', '').strip()
    price = request.args.get('price', '').strip()

    # Build search query
    murders = murders_advanced_search(name, collected, set_code, rarity, price)

    murders_data = [
        {
            'name': row[0],
            'collected': row[1],
            'collector_number': row[3],
            'image_url': row[4],
            'rarity': row[5],
            'greyscale': not row[1],  # True if not collected, for grayscale filtering
            'price': row[6]
        }
        for row in murders
    ]

    return render_template('murders/murders.html', murders=murders_data, show_search_tab=True, show_update_button=True, update_url='/update_murders')

@murders_bp.route('/update_murders', methods=['GET'])
@login_required
def update_murders():
    murders = murders_read_all()
    # print(outlaws)
  # Replace with your DB fetch logic
    return render_template('murders/update_murders.html', murders=murders)

@murders_bp.route('/process_update_murders', methods=['POST'])
@login_required
def process_update_murders():
    try:
        updates = request.form.to_dict(flat=True)  # Convert form data to dictionary
        # print(updates)  # Debugging: Check structure of form data

        # Iterate over the form data and update each card in the database
        for collector_number, collected_count in updates.items():
            update_murders_card(collector_number, int(collected_count))  # Use collector_number to update database

        flash("Murders collection updated successfully!", "success")
    except Exception as e:
        flash(f"Error updating murders: {str(e)}", "danger")
    return redirect(url_for('update_murders'))

@murders_bp.route('/export_murders_csv', methods=['GET'])
@login_required
def export_murders_csv():
    DB_PATH = current_app.config['DB_PATH']
    conn = sqlite3.connect(DB_PATH)

    cursor = conn.cursor()
    cursor.execute("SELECT name, set_code, collector_number, collected FROM murders")
    rows = cursor.fetchall()
    conn.close()

    # Generate CSV
    csv_data = io.StringIO()
    writer = csv.writer(csv_data)
    writer.writerow(['name', 'set', 'collector_number', 'collected', 'image_url'])
    writer.writerows(rows)
    csv_data.seek(0)

    # Return as file
    return Response(
        csv_data.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=murders_collection.csv"}
    )

@murders_bp.route('/export_murders_sql', methods=['GET'])
@login_required
def export_murders_sql():
    DB_PATH = current_app.config['DB_PATH']
    conn = sqlite3.connect(DB_PATH)

    cursor = conn.cursor()
    cursor.execute("SELECT name, set_code, collector_number, collected FROM murders")
    rows = cursor.fetchall()
    conn.close()

    # Generate SQL commands
    sql_data = io.StringIO()
    for row in rows:
        sql_data.write(f"INSERT OR REPLACE INTO murders (name, set_code, collector_number, collected) "
                       f"VALUES ('{row[0]}', '{row[1]}', {row[2]}, {row[3]});\n")
    sql_data.seek(0)

    # Return as file
    return Response(
        sql_data.getvalue(),
        mimetype="text/plain",
        headers={"Content-Disposition": "attachment;filename=murders_collection.sql"}
    )

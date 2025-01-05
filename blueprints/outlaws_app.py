import sqlite3,csv, io
from flask import current_app

from flask import Blueprint, render_template, request, redirect, url_for, flash, Response
from flask_login import login_required
from db_files.standard.outlaws_db import (
    outlaws_read_all,
    outlaws_advanced_search,
    update_outlaw_card
)
from utils.image_fix import process_updated_images

# Blueprint Definition
outlaws_bp = Blueprint('outlaws', __name__, template_folder='templates', static_folder='static')

# Routes
@outlaws_bp.route('/collections/otj', methods=['GET'])
def outlaws():
    name = request.args.get('name', '').strip()
    collected = request.args.get('collected', '').strip()
    set_code = request.args.get('full_set', '').strip()
    rarity = request.args.get('rarity', '').strip()
    price = request.args.get('price', '').strip()

    # Build search query
    outlaws = outlaws_advanced_search(name, collected, set_code, rarity, price)

    outlaws_data = [
        {
            'name': row[0],
            'collected': row[1],
            'collector_number': row[3],
            'image_url': row[4],
            'rarity': row[5],
            'greyscale': not row[1],  # True if not collected
            'price': row[6]
        }
        for row in outlaws
    ]

    return render_template(
        'outlaws/outlaws.html',
        outlaws=outlaws_data,
        show_search_tab=True,
        show_update_button=True,
        update_url='/update_outlaws'
    )

@outlaws_bp.route('/update_outlaws', methods=['GET', 'POST'])
@login_required
def update_outlaws():
    if request.method == 'POST':
        try:
            updates = request.form.to_dict(flat=True)

            # Process each card update
            for collector_number, collected_count in updates.items():
                update_outlaw_card(collector_number, int(collected_count))
                process_updated_images(name=None, set_code='OTJ', collector_number=collector_number)

            flash("Outlaws collection updated successfully!", "success")
        except Exception as e:
            flash(f"Error updating outlaws: {str(e)}", "danger")

        return redirect(url_for('outlaws.update_outlaws'))

    # Fetch outlaws data for GET request
    outlaws = outlaws_read_all()
    return render_template('outlaws/update_outlaws.html', outlaws=outlaws)

@outlaws_bp.route('/process_update_outlaws', methods=['POST'])
@login_required
def process_update_outlaws():
    try:
        updates = request.form.to_dict(flat=True)  # Convert form data to dictionary
        # print(updates)  # Debugging: Check structure of form data

        # Iterate over the form data and update each card in the database
        for collector_number, collected_count in updates.items():
            update_outlaw_card(collector_number, int(collected_count))  # Use collector_number to update database

        flash("Outlaws collection updated successfully!", "success")
    except Exception as e:
        flash(f"Error updating outlaws: {str(e)}", "danger")
    return redirect(url_for('update_outlaws'))

@outlaws_bp.route('/export_outlaws_csv', methods=['GET'])
@login_required
def export_outlaws_csv():
    try:
        DB_PATH = current_app.config['DB_PATH']
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT name, set_code, collector_number, collected FROM outlaws")
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
            headers={"Content-Disposition": "attachment;filename=outlaws_collection.csv"}
        )
    except Exception as e:
        flash(f"Error exporting Outlaws to CSV: {str(e)}", "danger")
        return redirect(url_for('outlaws.outlaws'))

@outlaws_bp.route('/export_outlaws_sql', methods=['GET'])
@login_required
def export_outlaws_sql():
    try:
        DB_PATH = current_app.config['DB_PATH']
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT name, set_code, collector_number, collected FROM outlaws")
        rows = cursor.fetchall()
        conn.close()

        # Generate SQL commands
        sql_data = io.StringIO()
        for row in rows:
            sql_data.write(
                f"INSERT OR REPLACE INTO outlaws (name, set_code, collector_number, collected) "
                f"VALUES ('{row[0]}', '{row[1]}', {row[2]}, {row[3]});\n"
            )
        sql_data.seek(0)

        # Return as file
        return Response(
            sql_data.getvalue(),
            mimetype="text/plain",
            headers={"Content-Disposition": "attachment;filename=outlaws_collection.sql"}
        )
    except Exception as e:
        flash(f"Error exporting Outlaws to SQL: {str(e)}", "danger")
        return redirect(url_for('outlaws.outlaws'))

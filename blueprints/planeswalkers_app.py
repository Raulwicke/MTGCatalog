import csv, io

from flask import Blueprint, render_template, request, redirect, url_for, flash, Response
from flask_login import login_required
from utils.image_fix import process_updated_images

from db_files.collections.pw_db import (
    planeswalker_read_all, 
    planeswalker_update, 
    planeswalker_advanced_search,
    get_planeswalker_by_name
)

planeswalkers_bp = Blueprint('planeswalkers', __name__, template_folder='templates', static_folder='static')


@planeswalkers_bp.route('/planeswalkers', methods=['GET'])
def catalog():
    name = request.args.get('name', '').strip()
    collected = request.args.get('collected', '').strip()
    set_code = request.args.get('set', '').strip()
    collector_number = request.args.get('collector_number', '').strip()
    price = request.args.get('price', '').strip()

    # print(f"DEBUG: Advanced Search - Name: {name}, Collected: {collected}, Set: {set_code}, Collector Number: {collector_number}")

    # Build search query
    planeswalkers = planeswalker_advanced_search(name, collected, set_code, collector_number)
    
    # Format data for the template
    planeswalkers_data = [
        {
            'name': row[0],
            'collected': row[1],
            'image_url': row[5],
            'greyscale': not row[1]  # True if not collected, for grayscale filtering
        }
        for row in planeswalkers
    ]
    
    return render_template('planeswalkers/catalog.html', planeswalkers=planeswalkers_data, show_search_tab=True, show_update_button=True, update_url='/update_planeswalkers')

@planeswalkers_bp.route('/update_planeswalkers', methods=['GET', 'POST'])
@login_required
def update_planeswalkers():
    if request.method == 'POST':
        planeswalker_updates = []

        for key, value in request.form.items():
            if key.startswith('planeswalkers['):
                index = int(key.split('[')[1].split(']')[0])
                field = key.split('[')[2].split(']')[0]

                while len(planeswalker_updates) <= index:
                    planeswalker_updates.append({})

                planeswalker_updates[index][field] = value

        for pw_data in planeswalker_updates:
            name = pw_data.get('name')
            collected = pw_data.get('collected', 'false') == 'true'
            collected_set = pw_data.get('collected_set', None)
            collector_number = pw_data.get('collector_number', None)

            # Handle empty fields: Fetch existing value or set NULL
            if collected_set == '':
                current_data = get_planeswalker_by_name(name)
                collected_set = current_data['collected_set'] or None

            if collector_number == '':
                current_data = get_planeswalker_by_name(name)
                collector_number = current_data['collector_number'] or None



            # Perform the update
            planeswalker_update(name, collected, collected_set, collector_number)
            if collected_set != '' or collector_number != '':
                process_updated_images(name, collected_set, collector_number=None)

        flash('All planeswalkers updated successfully!', 'success')
        return redirect(url_for('planeswalkers/update_planeswalkers'))

    planeswalkers = planeswalker_read_all()
    return render_template('update_planeswalkers.html', planeswalkers=planeswalkers)

@planeswalkers_bp.route('/export_csv')
@login_required
def export_csv():
    # Query all planeswalker data
    planeswalkers = planeswalker_read_all()
    
    # Use StringIO to write the CSV data in-memory
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write the header row
    writer.writerow(['Name', 'Collected', 'Set Code', 'Collected Set', 'Collector Number', 'Image URL'])
    
    # Write the data rows
    for row in planeswalkers:
        writer.writerow(row)
    
    # Move to the beginning of the StringIO buffer
    output.seek(0)
    
    # Return the response with the CSV file
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=planeswalkers.csv'}
    )

@planeswalkers_bp.route('/export_sql')
@login_required
def export_sql():
    planeswalkers = planeswalker_read_all()
    
    # Generate SQL commands to recreate data
    sql_commands = []
    sql_commands.append("BEGIN TRANSACTION;")
    sql_commands.append("DELETE FROM planeswalkers;")
    for row in planeswalkers:
        sql_commands.append(
            f"INSERT INTO planeswalkers (name, collected, set_code, collected_set, collector_number, image_url) "
            f"VALUES ('{row[0]}', {int(row[1])}, '{row[2]}', '{row[3]}', '{row[4]}', '{row[5]}');"
        )
    sql_commands.append("COMMIT;")
    
    # Combine SQL commands into a downloadable text file
    sql_output = "\n".join(sql_commands)
    return Response(
        sql_output,
        mimetype='text/plain',
        headers={'Content-Disposition': 'attachment;filename=planeswalkers.sql'}
    )


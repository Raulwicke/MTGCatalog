
from flask import (
                    Flask, 
                    render_template, 
                    redirect, 
                    request, 
                    url_for, 
                    flash,
                    Response)

from flask_login import (
                            LoginManager, 
                            UserMixin, 
                            login_user, 
                            logout_user, 
                            login_required, 
                            current_user)
from db_files.pw_db import (
    planeswalker_read_all, 
    planeswalker_update, 
    planeswalker_advanced_search,
    get_planeswalker_by_name
)

from db_files.user_db import(
    get_user_by_username, 
    get_user_by_id,
    )

from db_files.standard_db import(
    update_outlaw_card,
    outlaws_read_all,
    murders_read_all,
    update_murders_card
)
from db_files.database import db_path
from image_fix import process_updated_images
from werkzeug.security import check_password_hash

import csv
import os
import io
import sqlite3

app = Flask(__name__)

app.secret_key = os.getenv('SECRET_KEY', 'fallback-secret-key')

# Flask-Login setup
login_manager = LoginManager(app)
login_manager.session_protection = "strong"
login_manager.login_view = 'login'
login_manager.login_message_category = "info"


class User(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username

@login_manager.user_loader
def load_user(user_id):
    user = get_user_by_id(user_id)  # ***Replace this function with your own database query by user ID***
    if user:
        return User(user[0], user[1])
    return None

@app.route('/')
def home():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Count Planeswalkers
    cursor.execute('SELECT COUNT(*) FROM planeswalkers WHERE collected > 0')
    planeswalkers_collected = cursor.fetchone()[0]

    cursor.execute('SELECT COUNT(*) FROM planeswalkers')
    total_planeswalkers = cursor.fetchone()[0]

    conn.close()

    return render_template('home.html', planeswalkers_collected=planeswalkers_collected, total_planeswalkers=total_planeswalkers)

@app.route('/planeswalkers', methods=['GET'])
def catalog():
    name = request.args.get('name', '').strip()
    collected = request.args.get('collected', '').strip()
    set_code = request.args.get('set', '').strip()
    collector_number = request.args.get('collector_number', '').strip()

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
    
    return render_template('catalog.html', planeswalkers=planeswalkers_data)

@app.route('/collections/otj', methods=['GET'])
def outlaws():
    outlaws = outlaws_read_all()
    print(outlaws)
    outlaws_data = [
        {
            'name': row[0],
            'collected': row[1],
            'collector_number': row[3],
            'image_url': row[4],
            'greyscale': not row[1]  # True if not collected, for grayscale filtering
        }
        for row in outlaws
    ]
    return render_template('outlaws.html', outlaws=outlaws_data)

@app.route('/collections/mkm', methods=['GET'])
def murders():
    murders = murders_read_all()
    # print(outlaws)
    murders_data = [
        {
            'name': row[0],
            'collected': row[1],
            'collector_number': row[3],
            'image_url': row[4],
            'greyscale': not row[1]  # True if not collected, for grayscale filtering
        }
        for row in murders
    ]
    return render_template('murders.html', murders=murders_data)

@app.route('/search_outlaws', methods=['GET'])
def search_outlaws():
    name = request.args.get('name', '')
    set_code = request.args.get('set_code', '')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    query = 'SELECT * FROM outlaws WHERE 1=1'
    params = []

    if name:
        query += ' AND name LIKE ?'
        params.append(f'%{name}%')
    if set_code:
        query += ' AND set_code LIKE ?'
        params.append(f'%{set_code}%')

    cursor.execute(query, params)
    results = cursor.fetchall()
    conn.close()

    return render_template('outlaws.html', cards=results)

@app.route('/update_planeswalkers', methods=['GET', 'POST'])
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
            collected_set = pw_data.get('collected_set')
            collector_number = pw_data.get('collector_number')

            # Handle empty fields: Fetch existing value or set NULL
            if collected_set == '':
                current_data = get_planeswalker_by_name(name)
                collected_set = current_data['collected_set'] or None

            if collector_number == '':
                current_data = get_planeswalker_by_name(name)
                collector_number = current_data['collector_number'] or None

            # Perform the update
            planeswalker_update(name, collected, collected_set, collector_number)

        flash('All planeswalkers updated successfully!', 'success')
        return redirect(url_for('update_planeswalkers'))

    planeswalkers = planeswalker_read_all()
    return render_template('update_planeswalkers.html', planeswalkers=planeswalkers)

@app.route('/update_outlaws', methods=['GET'])
@login_required
def update_outlaws():
    outlaws = outlaws_read_all()
    print(outlaws)
  # Replace with your DB fetch logic
    return render_template('update_outlaws.html', outlaws=outlaws)

@app.route('/update_murders', methods=['GET'])
@login_required
def update_murders():
    murders = murders_read_all()
    # print(outlaws)
  # Replace with your DB fetch logic
    return render_template('update_murders.html', murders=murders)


@app.route('/process_update_outlaws', methods=['POST'])
@login_required
def process_update_outlaws():
    try:
        updates = request.form.to_dict(flat=True)  # Convert form data to dictionary
        print(updates)  # Debugging: Check structure of form data

        # Iterate over the form data and update each card in the database
        for collector_number, collected_count in updates.items():
            update_outlaw_card(collector_number, int(collected_count))  # Use collector_number to update database

        flash("Outlaws collection updated successfully!", "success")
    except Exception as e:
        flash(f"Error updating outlaws: {str(e)}", "danger")
    return redirect(url_for('update_outlaws'))

@app.route('/process_update_murders', methods=['POST'])
@login_required
def process_update_murders():
    try:
        updates = request.form.to_dict(flat=True)  # Convert form data to dictionary
        print(updates)  # Debugging: Check structure of form data

        # Iterate over the form data and update each card in the database
        for collector_number, collected_count in updates.items():
            update_murders_card(collector_number, int(collected_count))  # Use collector_number to update database

        flash("Murders collection updated successfully!", "success")
    except Exception as e:
        flash(f"Error updating murders: {str(e)}", "danger")
    return redirect(url_for('update_murders'))



@app.route('/export_csv')
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

@app.route('/export_sql')
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

@app.route('/export_outlaws_csv', methods=['GET'])
@login_required
def export_outlaws_csv():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name, set_code, collector_number, collected FROM outlaws")
    rows = cursor.fetchall()
    conn.close()

    # Generate CSV
    csv_data = io.StringIO()
    writer = csv.writer(csv_data)
    writer.writerow(['Name', 'Set Code', 'Collector Number', 'Collected'])
    writer.writerows(rows)
    csv_data.seek(0)

    # Return as file
    return Response(
        csv_data.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=outlaws_collection.csv"}
    )

@app.route('/export_outlaws_sql', methods=['GET'])
@login_required
def export_outlaws_sql():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name, set_code, collector_number, collected FROM outlaws")
    rows = cursor.fetchall()
    conn.close()

    # Generate SQL commands
    sql_data = io.StringIO()
    for row in rows:
        sql_data.write(f"INSERT OR REPLACE INTO outlaws (name, set_code, collector_number, collected) "
                       f"VALUES ('{row[0]}', '{row[1]}', {row[2]}, {row[3]});\n")
    sql_data.seek(0)

    # Return as file
    return Response(
        sql_data.getvalue(),
        mimetype="text/plain",
        headers={"Content-Disposition": "attachment;filename=outlaws_collection.sql"}
    )

@app.route('/export_murders_csv', methods=['GET'])
@login_required
def export_murders_csv():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name, set_code, collector_number, collected FROM murders")
    rows = cursor.fetchall()
    conn.close()

    # Generate CSV
    csv_data = io.StringIO()
    writer = csv.writer(csv_data)
    writer.writerow(['Name', 'Set Code', 'Collector Number', 'Collected'])
    writer.writerows(rows)
    csv_data.seek(0)

    # Return as file
    return Response(
        csv_data.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=murders_collection.csv"}
    )

@app.route('/export_murders_sql', methods=['GET'])
@login_required
def export_murders_sql():
    conn = sqlite3.connect(db_path)
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

@app.route('/login', methods=['GET', 'POST'])
def login():
    next_page = request.args.get('next') or request.referrer or url_for('home')  # Check for 'next', then referrer, then home
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        app.logger.info(f"Login attempt with username: {username}")
        
        # Fetch user details by username
        user = get_user_by_username(username)
        
        if user and check_password_hash(user[2], password):
            user_obj = User(user[0], user[1])
            login_user(user_obj)
            flash('Logged in successfully!', 'success')
            return redirect(next_page)  # Redirect to the appropriate next page
        else:
            flash('Invalid username or password.', 'danger')
    return render_template('login.html', next=next_page)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    next_page = request.referrer or url_for('home')  # Redirect to the previous page or home
    return redirect(next_page)


if __name__ == '__main__':
    app.run(debug=True)

from flask import Flask, render_template, redirect, request, url_for, flash
from flask_login import (
                            LoginManager, 
                            UserMixin, 
                            login_user, 
                            logout_user, 
                            login_required, 
                            current_user)
from database import planeswalker_read_all, planeswalker_update, get_user_by_username, get_user_by_id
from image_fix import process_updated_images
from werkzeug.security import check_password_hash


import os

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
def catalog():
    # Retrieve all planeswalkers
    planeswalkers = planeswalker_read_all()
    
    # Format data for the template
    planeswalkers_data = [
        {
            'name': row[0],
            'collected': row[1],
            'image_url': row[4],
            'greyscale': not row[1]  # True if not collected, for grayscale filtering
        }
        for row in planeswalkers
    ]
    
    return render_template('catalog.html', planeswalkers=planeswalkers_data)


@app.route('/update_planeswalkers', methods=['GET', 'POST'])
@login_required
def update_planeswalkers():
    if request.method == 'POST':
        name = request.form['name']
        collected = request.form['collected'] == 'true'
        collected_set = request.form['collected_set']
        planeswalker_update(name, collected, collected_set)
        # print(f"Name: {name}, Collected: {collected}, Set: {collected_set}")  # Debugging   
        process_updated_images(name, collected_set)
        flash(f'{name} updated successfully!', 'success')
        return redirect(url_for('catalog'))
    
    planeswalkers = planeswalker_read_all()
    return render_template('update_planeswalkers.html', planeswalkers=planeswalkers)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        app.logger.info(f"Login attempt with username: {username}")
        
        # Fetch user details by username
        user = get_user_by_username(username)  # ***Ensure this returns a tuple like (id, username, hashed_password)***
        
        if user and check_password_hash(user[2], password):
            user_obj = User(user[0], user[1])
            login_user(user_obj)
            flash('Logged in successfully!', 'success')
            return redirect(url_for('catalog'))
        else:
            flash('Invalid username or password.', 'danger')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('catalog'))

if __name__ == '__main__':
    app.run(debug=False)
import os

from flask import (
                    Flask, 
                    render_template, 
                    redirect, 
                    request, 
                    url_for, 
                    flash,
                    Response,
                    Blueprint,
                    current_app)

from flask_login import (
                            LoginManager, 
                            UserMixin, 
                            login_user, 
                            logout_user, 
                            login_required, 
                            current_user)

from db_files.auth.user_db import(
    get_user_by_username, 
    get_user_by_id,
    )

from werkzeug.security import check_password_hash

app = Flask(__name__)

app.secret_key = os.getenv('SECRET_KEY', 'fallback-secret-key')

# Flask-Login setup
login_manager = LoginManager(app)
login_manager.session_protection = "strong"
login_manager.login_view = 'login'
login_manager.login_message_category = "info"

auth_bp = Blueprint('auth', __name__, template_folder='templates', static_folder='static')

# ******************** #
# LOGIN/LOGOUT METHODS #
# ******************** #

class User(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username

@login_manager.user_loader
def load_user(user_id):
    user = get_user_by_id(user_id)  
    if user:
        return User(user[0], user[1])
    return None

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    next_page = request.args.get('next') or request.referrer or url_for('home')  # Check for 'next', then referrer, then home
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        current_app.logger.info(f"Login attempt with username: {username}")
        
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

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    next_page = request.referrer or url_for('home')  # Redirect to the previous page or home
    return redirect(next_page)
# ************** #
# ERROR HANDLING #
#  ************* #
@auth_bp.route('/error')
def error_page():
    return render_template('auth/in_progress.html'), 500

# Handle 404 Errors (Page Not Found)
@auth_bp.errorhandler(404)
def page_not_found(e):
    return render_template('auth/in_progress.html', error_message="Page Not Found!"), 404

# Handle 500 Errors (Internal Server Error)
@auth_bp.errorhandler(500)
def internal_server_error(e):
    return render_template('auth/in_progress.html', error_message="Internal Server Error!"), 500

# Handle All Other Uncaught Errors
@auth_bp.errorhandler(Exception)
def handle_exception(e):
    # Log the error for debugging purposes
    current_app.logger.error(f"Unhandled Exception: {e}")
    return render_template('auth/in_progress.html', error_message="An unexpected error occurred!"), 500

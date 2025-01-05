from flask import Blueprint, render_template, current_app
from db_files.standard.standard_db import fetch_collection_stats

# Blueprint Definition
home_bp = Blueprint('home', __name__, template_folder='templates', static_folder='static')

# Routes
@home_bp.route('/')
def home():
    try:
        # Fetch stats for display
        collection_stats = fetch_collection_stats()

        # Highlight featured sets or cards
        featured_sets = [
            {"name": "Outlaws of Thunder Junction", "url": "/outlaws", "image": "/static/images/outlaws_banner.jpg"},
            {"name": "Murders", "url": "/murders", "image": "/static/images/murders_banner.jpg"},
            {"name": "Planeswalkers", "url": "/planeswalkers", "image": "/static/images/planeswalkers_banner.jpg"}
        ]

        return render_template(
            'home.html',
            stats=collection_stats,
            featured_sets=featured_sets
        )
    except Exception as e:
        # Log error and redirect to an error page
        current_app.logger.error(f"Error loading home page: {e}")
        return render_template('error.html', message="Unable to load the home page.")

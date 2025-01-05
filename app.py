from flask import Flask
from blueprints.auth_app import auth_bp
from blueprints.home_app import home_bp
from blueprints.murders_app import murders_bp
from blueprints.outlaws_app import outlaws_bp
from blueprints.planeswalkers_app import planeswalkers_bp
from blueprints.pricing_app import pricing_bp
from blueprints.score_app import scores_bp
from config import AppConfig
import logging

# Create the Flask application
app = Flask(__name__)
app.config.from_object(AppConfig)

# Set up logging
logging.basicConfig(filename=app.config['LOG_FILE'], level=logging.INFO)
logger = logging.getLogger(__name__)

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(home_bp)
app.register_blueprint(murders_bp, url_prefix='/murders')
app.register_blueprint(outlaws_bp, url_prefix='/outlaws')
app.register_blueprint(planeswalkers_bp, url_prefix='/planeswalkers')
app.register_blueprint(pricing_bp, url_prefix='/pricing')
app.register_blueprint(scores_bp, url_prefix='/scores')

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    logger.error(f"404 Error: {e}")
    return "Page not found", 404

@app.errorhandler(500)
def internal_server_error(e):
    logger.error(f"500 Error: {e}")
    return "Internal server error", 500

if __name__ == '__main__':
    app.run(debug=AppConfig.DEBUG)

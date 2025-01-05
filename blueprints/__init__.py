from requests import *

from .outlaws_app import outlaws_bp
from .planeswalkers_app import planeswalkers_bp
# from .trades_app import trades_bp
from .auth_app import auth_bp
from .murders_app import murders_bp
from .score_app import scores_bp

def register_blueprints(app):
    app.register_blueprint(outlaws_bp, url_prefix='/outlaws')
    app.register_blueprint(planeswalkers_bp, url_prefix='/planeswalkers')
    app.register_blueprint(murders_bp, url_prefix='/murders')
    app.register_blueprint(scores_bp, url_prefix='/scores')
    app.register_blueprint(auth_bp, url_prefix='/auth')


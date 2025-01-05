import os

class Config:
    """Base configuration with default settings."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'fallback-secret-key')  # For session management and CSRF protection
    DEBUG = False
    TESTING = False
    DB_PATH = os.environ.get('DB_PATH', 'data/collection.db')         # Path to the main SQLite database
    SCHEMA_PATH = os.environ.get('SCHEMA_PATH', 'db_files/migrations/')  # Path to SQL schema migrations
    STATIC_FOLDER = 'static'                                         # Static files location
    TEMPLATES_FOLDER = 'templates'                                   # Templates folder location

    # API Configurations
    SCRYFALL_API_URL = 'https://api.scryfall.com/cards/named?fuzzy={name}&set={set_code}'
    SCRYFALL_TIMEOUT = 5  # Timeout for API calls in seconds

    # Pagination Defaults
    ITEMS_PER_PAGE = 20

    # Logging
    LOG_FILE = os.environ.get('LOG_FILE', 'logs/app.log')

class DevelopmentConfig(Config):
    """Development-specific settings."""
    DEBUG = True
    DB_PATH = os.environ.get('DB_PATH', 'data/dev_collection.db')

class TestingConfig(Config):
    """Testing-specific settings."""
    TESTING = True
    DB_PATH = os.environ.get('DB_PATH', 'data/test_collection.db')

class ProductionConfig(Config):
    """Production-specific settings."""
    DEBUG = False
    DB_PATH = os.environ.get('DB_PATH', 'data/prod_collection.db')
    SECRET_KEY = os.environ.get('SECRET_KEY')  # Ensure a strong secret key is set in production

# Select the appropriate configuration based on the environment
config_map = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
}
current_env = os.environ.get('FLASK_ENV', 'development')
AppConfig = config_map[current_env]

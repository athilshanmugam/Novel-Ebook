import os
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception as e:
    print(f"Warning: Could not load .env file: {e}")

class Config:
    """Base configuration class"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DATABASE_URL = os.environ.get('DATABASE_URL') or 'names.db'
    FLASK_ENV = os.environ.get('FLASK_ENV') or 'development'
    FLASK_DEBUG = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    
    # Server configuration
    HOST = os.environ.get('HOST') or '0.0.0.0'
    PORT = int(os.environ.get('PORT') or 5000)
    
    # URLs
    PRODUCTION_URL = os.environ.get('PRODUCTION_URL') or 'https://novel-ebook.onrender.com'
    LOCAL_URL = os.environ.get('LOCAL_URL') or 'http://localhost:5000'
    
    # CORS configuration
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', 'http://localhost:3000,http://localhost:5000,https://novel-ebook.onrender.com').split(',')
    
    # Logging
    LOG_LEVEL = os.environ.get('LOG_LEVEL') or 'INFO'

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    FLASK_DEBUG = True

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    FLASK_DEBUG = False

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DATABASE_URL = ':memory:'

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
} 
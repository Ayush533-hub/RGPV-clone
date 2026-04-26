"""
Configuration file for RGPV Flask Application
Separates configuration logic from application code
"""

import os
from dotenv import load_dotenv
from datetime import timedelta

# Load environment variables from .env
load_dotenv()

class Config:
    """Base configuration"""
    # Flask
    FLASK_APP = os.getenv("FLASK_APP", "app.py")
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///data.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Server
    HOST = os.getenv("HOST", "127.0.0.1")
    PORT = int(os.getenv("PORT", 5000))
    
    # Session
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = os.getenv("LOG_FILE", "logs/app.log")
    LOG_MAX_SIZE = int(os.getenv("LOG_MAX_SIZE", 10485760))  # 10MB
    LOG_BACKUP_COUNT = int(os.getenv("LOG_BACKUP_COUNT", 10))
    
    # Security
    MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH", 16777216))  # 16MB
    REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", 30))
    
    # CORS
    CORS_ALLOW_ALL = os.getenv("CORS_ALLOW_ALL", "False").lower() == "true"
    ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False
    SESSION_COOKIE_SECURE = False
    CORS_ALLOW_ALL = True  # Allow all origins in development

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = True  # HTTPS only
    CORS_ALLOW_ALL = False  # Whitelist origins only
    
    # Production security checks
    SECRET_KEY = os.getenv("SECRET_KEY")
    if not SECRET_KEY or SECRET_KEY == "dev-secret-key":
        raise ValueError("ERROR: SECRET_KEY must be set in production!")

class TestingConfig(Config):
    """Testing configuration"""
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SESSION_COOKIE_SECURE = False

def get_config(env=None):
    """Get appropriate configuration class"""
    if env is None:
        env = os.getenv("FLASK_ENV", "development")
    
    config_map = {
        "development": DevelopmentConfig,
        "production": ProductionConfig,
        "testing": TestingConfig,
    }
    
    config_class = config_map.get(env, DevelopmentConfig)
    print(f"Loaded {config_class.__name__} for environment: {env}")
    return config_class

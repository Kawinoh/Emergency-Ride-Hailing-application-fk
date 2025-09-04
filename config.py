"""
Configuration settings for Emergency Ride-Hailing Application
"""

import os
from datetime import timedelta

class Config:
    """Base configuration class"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here-change-this-in-production'
    MONGODB_URI = os.environ.get('MONGODB_URI') or 'mongodb://localhost:27017/emergency_ride_hailing'
    GOOGLE_MAPS_API_KEY = os.environ.get('GOOGLE_MAPS_API_KEY') or 'your-google-maps-api-key-here'
    
    # Session configuration
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    
    # Socket.IO configuration
    SOCKETIO_ASYNC_MODE = 'eventlet'
    
    # Application settings
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    
    # Emergency request settings
    MAX_EMERGENCY_REQUESTS_PER_USER = 3  # Max pending requests per user
    EMERGENCY_REQUEST_TIMEOUT = 300  # 5 minutes timeout for emergency requests
    
    # Driver settings
    MAX_DRIVER_SEARCH_RADIUS = 50  # Maximum search radius in kilometers
    DRIVER_LOCATION_UPDATE_INTERVAL = 30  # Update driver location every 30 seconds

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False
    
    # Override with production values
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY environment variable must be set in production")

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    MONGODB_URI = 'mongodb://localhost:27017/emergency_ride_hailing_test'

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

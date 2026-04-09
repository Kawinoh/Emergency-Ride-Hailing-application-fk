"""
Fixed configuration settings for Emergency Ride-Hailing Application
"""

import os
from datetime import timedelta
import secrets

def get_config():
    """Get configuration based on environment"""
    env = os.environ.get('FLASK_ENV', 'development')
    
    class Config:
        """Base configuration class"""
        SECRET_KEY = os.environ.get('SECRET_KEY') or secrets.token_hex(32)
        MONGODB_URI = os.environ.get('MONGODB_URI') or 'mongodb://localhost:27017/emergency_ride_hailing'
        GOOGLE_MAPS_API_KEY = os.environ.get('GOOGLE_MAPS_API_KEY')
        
        # Session configuration
        PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
        
        # Socket.IO configuration
        SOCKETIO_ASYNC_MODE = 'threading'
        
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
        
        @property
        def SECRET_KEY(self):
            key = os.environ.get('SECRET_KEY')
            if not key:
                raise ValueError("SECRET_KEY environment variable must be set in production")
            return key
        
        @property
        def MONGODB_URI(self):
            uri = os.environ.get('MONGODB_URI')
            if not uri:
                raise ValueError("MONGODB_URI environment variable must be set in production")
            return uri

    class TestingConfig(Config):
        """Testing configuration"""
        TESTING = True
        MONGODB_URI = 'mongodb://localhost:27017/emergency_ride_hailing_test'

    config_map = {
        'development': DevelopmentConfig,
        'production': ProductionConfig,
        'testing': TestingConfig,
        'default': DevelopmentConfig
    }
    
    return config_map.get(env, DevelopmentConfig)()

# Create the config instance
config = get_config()

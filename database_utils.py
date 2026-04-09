"""
Database utilities and indexing for Emergency Ride-Hailing Application
"""

from pymongo import MongoClient, ASCENDING, DESCENDING, GEO2D, GEOSPHERE
from bson import ObjectId
import os
from datetime import datetime
from config import config

class DatabaseManager:
    """Database management class with optimized operations"""
    
    def __init__(self, config_name='development'):
        """Initialize database connection and collections"""
        self.config_name = config_name
        self.app_config = config[config_name]
        self.client = MongoClient(
            self.app_config.MONGODB_URI, 
            maxPoolSize=50, 
            connectTimeoutMS=30000,
            serverSelectionTimeoutMS=30000
        )
        self.db = self.client.get_database()
        self.setup_collections()
    
    def setup_collections(self):
        """Setup collection references"""
        self.users = self.db.users
        self.drivers = self.db.drivers
        self.rides = self.db.rides
        self.emergency_requests = self.db.emergency_requests
    
    def create_indexes(self):
        """Create optimized indexes for all collections"""
        print("Creating database indexes...")
        
        # Users collection indexes
        self.users.create_index([
            ("email", ASCENDING)
        ], unique=True, name="email_unique")
        
        self.users.create_index([
            ("phone", ASCENDING)
        ], unique=True, sparse=True, name="phone_unique")
        
        self.users.create_index([
            ("created_at", DESCENDING)
        ], name="created_at_desc")
        
        # Drivers collection indexes
        self.drivers.create_index([
            ("email", ASCENDING)
        ], unique=True, name="driver_email_unique")
        
        self.drivers.create_index([
            ("phone", ASCENDING)
        ], unique=True, sparse=True, name="driver_phone_unique")
        
        self.drivers.create_index([
            ("location", GEOSPHERE)
        ], name="driver_location_geosphere")
        
        self.drivers.create_index([
            ("is_available", ASCENDING),
            ("location", GEOSPHERE)
        ], name="driver_available_location")
        
        self.drivers.create_index([
            ("is_online", ASCENDING)
        ], name="driver_online_status")
        
        # Emergency requests collection indexes
        self.emergency_requests.create_index([
            ("user_id", ASCENDING)
        ], name="emergency_user_id")
        
        self.emergency_requests.create_index([
            ("status", ASCENDING),
            ("created_at", DESCENDING)
        ], name="emergency_status_created")
        
        self.emergency_requests.create_index([
            ("pickup_location", GEOSPHERE)
        ], name="emergency_pickup_location")
        
        self.emergency_requests.create_index([
            ("emergency_type", ASCENDING),
            ("status", ASCENDING)
        ], name="emergency_type_status")
        
        self.emergency_requests.create_index([
            ("created_at", DESCENDING)
        ], name="emergency_created_desc")
        
        # Rides collection indexes
        self.rides.create_index([
            ("emergency_request_id", ASCENDING)
        ], name="ride_emergency_request")
        
        self.rides.create_index([
            ("driver_id", ASCENDING)
        ], name="ride_driver_id")
        
        self.rides.create_index([
            ("user_id", ASCENDING)
        ], name="ride_user_id")
        
        self.rides.create_index([
            ("status", ASCENDING),
            ("created_at", DESCENDING)
        ], name="ride_status_created")
        
        self.rides.create_index([
            ("created_at", DESCENDING)
        ], name="ride_created_desc")
        
        print("Database indexes created successfully!")
    
    def find_nearest_drivers(self, latitude, longitude, max_distance_km=10, limit=5):
        """Find nearest available drivers using geospatial query"""
        # Convert km to radians for MongoDB
        max_distance_rad = max_distance_km / 6371
        
        return list(self.drivers.find([
            ("is_available", True),
            ("is_online", True),
            ("location", {
                "$near": {
                    "$geometry": {
                        "type": "Point",
                        "coordinates": [longitude, latitude]
                    },
                    "$maxDistance": max_distance_rad
                }
            })
        ]).limit(limit))
    
    def get_active_emergency_requests(self, limit=50):
        """Get active emergency requests with optimized query"""
        return list(self.emergency_requests.find({
            "status": {"$in": ["pending", "assigned"]}
        }).sort("created_at", DESCENDING).limit(limit))
    
    def get_user_statistics(self):
        """Get user statistics for dashboard"""
        pipeline = [
            {"$group": {
                "_id": "$status",
                "count": {"$sum": 1}
            }}
        ]
        return list(self.emergency_requests.aggregate(pipeline))
    
    def cleanup_old_requests(self, days_old=7):
        """Clean up old completed emergency requests"""
        cutoff_date = datetime.now() - timedelta(days=days_old)
        result = self.emergency_requests.delete_many({
            "status": "completed",
            "created_at": {"$lt": cutoff_date}
        })
        print(f"Cleaned up {result.deleted_count} old emergency requests")
        return result.deleted_count
    
    def create_sample_admin(self):
        """Create sample admin user for development"""
        if self.config_name == 'development':
            from werkzeug.security import generate_password_hash
            
            existing_admin = self.users.find_one({"email": "admin@emergencyride.com"})
            if not existing_admin:
                admin_user = {
                    "email": "admin@emergencyride.com",
                    "password": generate_password_hash("admin123"),
                    "name": "System Administrator",
                    "user_type": "admin",
                    "is_active": True,
                    "created_at": datetime.now()
                }
                self.users.insert_one(admin_user)
                print("Sample admin user created: admin@emergencyride.com / admin123")
            else:
                print("Admin user already exists")
    
    def close_connection(self):
        """Close database connection"""
        self.client.close()

def initialize_database(config_name='development'):
    """Initialize database with indexes and sample data"""
    db_manager = DatabaseManager(config_name)
    
    try:
        # Create indexes
        db_manager.create_indexes()
        
        # Create sample admin for development
        db_manager.create_sample_admin()
        
        print(f"Database initialized successfully for {config_name} environment!")
        
    except Exception as e:
        print(f"Database initialization error: {e}")
        raise
    finally:
        db_manager.close_connection()

if __name__ == "__main__":
    # Initialize database with default development config
    config_name = os.environ.get('FLASK_ENV', 'development')
    initialize_database(config_name)

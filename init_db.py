#!/usr/bin/env python3
"""
Database initialization script for Emergency Ride-Hailing Application
"""

from pymongo import MongoClient
from werkzeug.security import generate_password_hash
from datetime import datetime
import os

def init_database():
    """Initialize the database with sample data"""
    
    # Connect to MongoDB
    client = MongoClient('mongodb://localhost:27017/')
    db = client.emergency_ride_hailing
    
    # Collections
    users = db.users
    drivers = db.drivers
    rides = db.rides
    emergency_requests = db.emergency_requests
    
    print("Initializing Emergency Ride-Hailing Database...")
    
    # Create indexes
    print("Creating database indexes...")
    users.create_index("email", unique=True)
    drivers.create_index("email", unique=True)
    drivers.create_index("license_number", unique=True)
    emergency_requests.create_index("user_id")
    emergency_requests.create_index("assigned_driver")
    emergency_requests.create_index("status")
    rides.create_index("user_id")
    rides.create_index("driver_id")
    rides.create_index("status")
    
    # Create sample admin user
    admin_user = {
        'name': 'Admin User',
        'email': 'admin@emergencyride.com',
        'password': generate_password_hash('admin123'),
        'phone': '+1234567890',
        'role': 'admin',
        'created_at': datetime.utcnow()
    }
    
    if not users.find_one({'email': 'admin@emergencyride.com'}):
        users.insert_one(admin_user)
        print("✓ Created admin user (admin@emergencyride.com / admin123)")
    else:
        print("✓ Admin user already exists")
    
    # Create sample regular user
    sample_user = {
        'name': 'John Doe',
        'email': 'user@example.com',
        'password': generate_password_hash('user123'),
        'phone': '+1234567891',
        'created_at': datetime.utcnow(),
        'emergency_contacts': [
            {'name': 'Jane Doe', 'phone': '+1234567892', 'relationship': 'Spouse'},
            {'name': 'Emergency Contact', 'phone': '+1234567893', 'relationship': 'Friend'}
        ]
    }
    
    if not users.find_one({'email': 'user@example.com'}):
        users.insert_one(sample_user)
        print("✓ Created sample user (user@example.com / user123)")
    else:
        print("✓ Sample user already exists")
    
    # Create sample driver
    sample_driver = {
        'name': 'Mike Johnson',
        'email': 'driver@example.com',
        'password': generate_password_hash('driver123'),
        'phone': '+1234567894',
        'license_number': 'DL123456789',
        'vehicle_info': {
            'make': 'Toyota',
            'model': 'Camry',
            'year': 2020,
            'color': 'Silver',
            'plate_number': 'ABC123'
        },
        'is_available': True,
        'current_location': {
            'latitude': 40.7128,
            'longitude': -74.0060
        },
        'rating': 4.8,
        'total_rides': 0,
        'created_at': datetime.utcnow()
    }
    
    if not drivers.find_one({'email': 'driver@example.com'}):
        drivers.insert_one(sample_driver)
        print("✓ Created sample driver (driver@example.com / driver123)")
    else:
        print("✓ Sample driver already exists")
    
    # Create another sample driver
    sample_driver2 = {
        'name': 'Sarah Wilson',
        'email': 'driver2@example.com',
        'password': generate_password_hash('driver123'),
        'phone': '+1234567895',
        'license_number': 'DL987654321',
        'vehicle_info': {
            'make': 'Honda',
            'model': 'Civic',
            'year': 2019,
            'color': 'Blue',
            'plate_number': 'XYZ789'
        },
        'is_available': False,
        'current_location': {
            'latitude': 40.7589,
            'longitude': -73.9851
        },
        'rating': 4.6,
        'total_rides': 0,
        'created_at': datetime.utcnow()
    }
    
    if not drivers.find_one({'email': 'driver2@example.com'}):
        drivers.insert_one(sample_driver2)
        print("✓ Created sample driver 2 (driver2@example.com / driver123)")
    else:
        print("✓ Sample driver 2 already exists")
    
    print("\nDatabase initialization completed!")
    print("\nSample accounts created:")
    print("Admin: admin@emergencyride.com / admin123")
    print("User: user@example.com / user123")
    print("Driver: driver@example.com / driver123")
    print("Driver 2: driver2@example.com / driver123")
    
    print("\nNext steps:")
    print("1. Run the application: python run.py")
    print("2. Open http://localhost:5000")
    print("3. Login with any of the sample accounts")

if __name__ == '__main__':
    try:
        init_database()
    except Exception as e:
        print(f"Error initializing database: {e}")
        print("Please ensure MongoDB is running on localhost:27017")

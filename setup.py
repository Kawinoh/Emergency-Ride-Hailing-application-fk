#!/usr/bin/env python3
"""
Setup script for Emergency Ride-Hailing Application
"""

import os
import sys
import subprocess
from pathlib import Path

def check_python_version():
    """Check if Python version is 3.8 or higher"""
    if sys.version_info < (3, 8):
        print("Error: Python 3.8 or higher is required")
        sys.exit(1)
    print(f"✓ Python {sys.version.split()[0]} detected")

def install_requirements():
    """Install required packages"""
    print("Installing required packages...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✓ Requirements installed successfully")
    except subprocess.CalledProcessError:
        print("Error: Failed to install requirements")
        sys.exit(1)

def create_directories():
    """Create necessary directories"""
    directories = [
        "static/css",
        "static/js",
        "static/images",
        "templates",
        "logs"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✓ Created directory: {directory}")

def check_mongodb():
    """Check if MongoDB is available"""
    try:
        from pymongo import MongoClient
        client = MongoClient('mongodb://localhost:27017/')
        client.admin.command('ping')
        print("✓ MongoDB connection successful")
        return True
    except Exception as e:
        print(f"⚠ MongoDB connection failed: {e}")
        print("Please ensure MongoDB is running on localhost:27017")
        return False

def create_env_file():
    """Create .env file with default values"""
    env_content = """# Emergency Ride-Hailing Application Configuration
SECRET_KEY=your-secret-key-here-change-this-in-production
MONGODB_URI=mongodb://localhost:27017/emergency_ride_hailing
GOOGLE_MAPS_API_KEY=your-google-maps-api-key-here

# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True
"""
    
    if not os.path.exists('.env'):
        with open('.env', 'w') as f:
            f.write(env_content)
        print("✓ Created .env file with default configuration")
        print("⚠ Please update the .env file with your actual API keys and configuration")
    else:
        print("✓ .env file already exists")

def main():
    """Main setup function"""
    print("Emergency Ride-Hailing Application Setup")
    print("=" * 40)
    
    # Check Python version
    check_python_version()
    
    # Create directories
    create_directories()
    
    # Install requirements
    install_requirements()
    
    # Check MongoDB
    mongodb_available = check_mongodb()
    
    # Create .env file
    create_env_file()
    
    print("\n" + "=" * 40)
    print("Setup completed!")
    print("\nNext steps:")
    print("1. Update the .env file with your configuration")
    print("2. Get a Google Maps API key and update the templates")
    if not mongodb_available:
        print("3. Start MongoDB service")
    print("4. Run the application: python app.py")
    print("5. Open http://localhost:5000 in your browser")
    
    print("\nFor more information, see README.md")

if __name__ == "__main__":
    main()

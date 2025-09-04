#!/usr/bin/env python3
"""
Run script for Emergency Ride-Hailing Application
"""

import os
import sys
from app import app, socketio

def main():
    """Main function to run the application"""
    # Set default environment
    if not os.environ.get('FLASK_ENV'):
        os.environ['FLASK_ENV'] = 'development'
    
    # Get configuration
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '0.0.0.0')
    debug = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    
    print("Emergency Ride-Hailing Application")
    print("=" * 40)
    print(f"Environment: {os.environ.get('FLASK_ENV', 'development')}")
    print(f"Host: {host}")
    print(f"Port: {port}")
    print(f"Debug: {debug}")
    print("=" * 40)
    print("Starting server...")
    print(f"Access the application at: http://{host}:{port}")
    print("Press Ctrl+C to stop the server")
    print("=" * 40)
    
    try:
        # Run the application with Socket.IO
        socketio.run(
            app,
            host=host,
            port=port,
            debug=debug,
            allow_unsafe_werkzeug=True,
            use_reloader=False
        )
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        print(f"Error starting server: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()

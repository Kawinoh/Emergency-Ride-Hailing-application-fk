#!/usr/bin/env python3
"""
Improved run script for Emergency Ride-Hailing Application
"""

import os
import sys

def main():
    """Main function to run the application"""
    try:
        # Import here to avoid circular imports
        from app import app, socketio
        from error_handlers import setup_logging, setup_error_handlers
        from config import config
        
        # Load configuration
        config_name = os.environ.get('FLASK_ENV', 'development')
        app.config.from_object(config[config_name])
        
        # Setup logging
        setup_logging(app)
        
        # Setup error handlers
        setup_error_handlers(app)
        
        # Get port from environment or use default
        port = int(os.environ.get('PORT', 5000))
        
        # Get host from environment or use default
        host = os.environ.get('HOST', '0.0.0.0')
        
        # Get debug mode
        debug = app.config.get('DEBUG', False)
        
        # Print startup information
        print("=" * 60)
        print("Emergency Ride-Hailing Application")
        print("=" * 60)
        print(f"Environment: {config_name}")
        print(f"Host: {host}")
        print(f"Port: {port}")
        print(f"Debug Mode: {debug}")
        print(f"Access URL: http://{host}:{port}")
        print("=" * 60)
        print("Starting server...")
        print("Press Ctrl+C to stop the server")
        print("=" * 60)
        
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
    except ImportError as e:
        print(f"Import error: {e}")
        print("Please ensure all dependencies are installed: pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"Error starting server: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()

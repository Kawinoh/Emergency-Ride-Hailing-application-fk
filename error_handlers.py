"""
Error handlers and logging for Emergency Ride-Hailing Application
"""

import logging
import traceback
from datetime import datetime
from flask import jsonify, render_template, request, current_app
from functools import wraps

# Configure logging
def setup_logging(app):
    """Setup application logging"""
    
    # Create logs directory if it doesn't exist
    import os
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    # Configure logging format
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]',
        handlers=[
            logging.FileHandler(f'logs/emergency_ride_{datetime.now().strftime("%Y%m%d")}.log'),
            logging.StreamHandler()
        ]
    )
    
    app.logger.setLevel(logging.INFO)
    app.logger.info('Emergency Ride-Hailing Application startup')

class DatabaseError(Exception):
    """Custom exception for database errors"""
    pass

class AuthenticationError(Exception):
    """Custom exception for authentication errors"""
    pass

class ValidationError(Exception):
    """Custom exception for validation errors"""
    pass

class EmergencyError(Exception):
    """Custom exception for emergency-related errors"""
    pass

def log_error(error_type, message, details=None):
    """Log error with details"""
    error_data = {
        'timestamp': datetime.now().isoformat(),
        'type': error_type,
        'message': message,
        'details': details or {}
    }
    
    logging.error(f"{error_type}: {message} - Details: {details}")
    return error_data

def handle_database_errors(f):
    """Decorator to handle database errors"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            error_details = {
                'function': f.__name__,
                'args': str(args),
                'kwargs': str(kwargs),
                'traceback': traceback.format_exc()
            }
            log_error('DatabaseError', str(e), error_details)
            return jsonify({
                'success': False,
                'message': 'Database operation failed',
                'error': str(e)
            }), 500
    return decorated_function

def handle_validation_errors(f):
    """Decorator to handle validation errors"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except ValidationError as e:
            log_error('ValidationError', str(e))
            return jsonify({
                'success': False,
                'message': str(e),
                'error_type': 'validation'
            }), 400
        except Exception as e:
            log_error('UnexpectedError', str(e))
            return jsonify({
                'success': False,
                'message': 'An unexpected error occurred',
                'error_type': 'unexpected'
            }), 500
    return decorated_function

def setup_error_handlers(app):
    """Setup Flask error handlers"""
    
    @app.errorhandler(404)
    def not_found_error(error):
        if request.path.startswith('/api/'):
            return jsonify({
                'success': False,
                'message': 'Endpoint not found',
                'error_code': 404
            }), 404
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        log_error('InternalServerError', str(error), {
            'path': request.path,
            'method': request.method,
            'traceback': traceback.format_exc()
        })
        
        if request.path.startswith('/api/'):
            return jsonify({
                'success': False,
                'message': 'Internal server error',
                'error_code': 500
            }), 500
        return render_template('errors/500.html'), 500
    
    @app.errorhandler(403)
    def forbidden_error(error):
        if request.path.startswith('/api/'):
            return jsonify({
                'success': False,
                'message': 'Access forbidden',
                'error_code': 403
            }), 403
        return render_template('errors/403.html'), 403
    
    @app.errorhandler(401)
    def unauthorized_error(error):
        if request.path.startswith('/api/'):
            return jsonify({
                'success': False,
                'message': 'Unauthorized access',
                'error_code': 401
            }), 401
        return render_template('errors/401.html'), 401

class PerformanceMonitor:
    """Monitor application performance"""
    
    def __init__(self):
        self.requests = []
        self.slow_queries = []
    
    def log_request(self, endpoint, duration, status_code):
        """Log request performance"""
        request_data = {
            'endpoint': endpoint,
            'duration': duration,
            'status_code': status_code,
            'timestamp': datetime.now()
        }
        
        self.requests.append(request_data)
        
        # Log slow requests (> 1 second)
        if duration > 1.0:
            log_error('SlowRequest', f"Slow request detected: {endpoint}", {
                'duration': duration,
                'status_code': status_code
            })
    
    def log_slow_query(self, query, duration):
        """Log slow database queries"""
        query_data = {
            'query': str(query),
            'duration': duration,
            'timestamp': datetime.now()
        }
        
        self.slow_queries.append(query_data)
        log_error('SlowQuery', f"Slow database query detected", {
            'duration': duration,
            'query': str(query)
        })
    
    def get_performance_stats(self):
        """Get performance statistics"""
        if not self.requests:
            return {}
        
        total_requests = len(self.requests)
        avg_duration = sum(r['duration'] for r in self.requests) / total_requests
        max_duration = max(r['duration'] for r in self.requests)
        
        return {
            'total_requests': total_requests,
            'average_duration': avg_duration,
            'max_duration': max_duration,
            'slow_queries': len(self.slow_queries)
        }

# Global performance monitor instance
performance_monitor = PerformanceMonitor()

def monitor_performance(f):
    """Decorator to monitor function performance"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        start_time = datetime.now()
        try:
            result = f(*args, **kwargs)
            duration = (datetime.now() - start_time).total_seconds()
            performance_monitor.log_request(request.endpoint, duration, 200)
            return result
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            performance_monitor.log_request(request.endpoint, duration, 500)
            raise
    return decorated_function

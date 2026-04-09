"""
Shared utilities for Emergency Ride-Hailing Application
"""

import math
from datetime import datetime, timedelta
from flask import flash, redirect, url_for
from functools import wraps
import re

def calculate_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the distance between two coordinates using Haversine formula
    
    Args:
        lat1, lon1: First point coordinates (latitude, longitude)
        lat2, lon2: Second point coordinates (latitude, longitude)
    
    Returns:
        float: Distance in kilometers
    """
    R = 6371  # Radius of the Earth in kilometers
    
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    
    a = (math.sin(dlat/2) * math.sin(dlat/2) + 
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * 
         math.sin(dlon/2) * math.sin(dlon/2))
    
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    distance = R * c
    
    return distance

def validate_email(email):
    """
    Validate email format
    
    Args:
        email (str): Email address to validate
    
    Returns:
        bool: True if valid, False otherwise
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_phone(phone):
    """
    Validate phone number format (international format)
    
    Args:
        phone (str): Phone number to validate
    
    Returns:
        bool: True if valid, False otherwise
    """
    # Remove any non-digit characters
    clean_phone = re.sub(r'[^\d+]', '', phone)
    # Check if it starts with + and has 10-15 digits
    return bool(re.match(r'^\+\d{10,15}$', clean_phone))

def validate_password_strength(password):
    """
    Validate password strength
    
    Args:
        password (str): Password to validate
    
    Returns:
        tuple: (is_valid, error_message)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    
    if not re.search(r'\d', password):
        return False, "Password must contain at least one number"
    
    return True, ""

def format_datetime(dt, format_str='%Y-%m-%d %H:%M:%S'):
    """
    Format datetime object to string
    
    Args:
        dt (datetime): Datetime object
        format_str (str): Format string
    
    Returns:
        str: Formatted datetime string
    """
    if isinstance(dt, datetime):
        return dt.strftime(format_str)
    return str(dt)

def get_time_ago(dt):
    """
    Get human-readable time ago string
    
    Args:
        dt (datetime): Datetime object
    
    Returns:
        str: Time ago string (e.g., "2 hours ago")
    """
    if not isinstance(dt, datetime):
        return "Unknown"
    
    now = datetime.now()
    diff = now - dt
    
    if diff.days > 365:
        years = diff.days // 365
        return f"{years} year{'s' if years > 1 else ''} ago"
    elif diff.days > 30:
        months = diff.days // 30
        return f"{months} month{'s' if months > 1 else ''} ago"
    elif diff.days > 0:
        return f"{diff.days} day{'s' if diff.days > 1 else ''} ago"
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f"{hours} hour{'s' if hours > 1 else ''} ago"
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
    else:
        return "Just now"

def sanitize_input(text):
    """
    Sanitize user input to prevent XSS
    
    Args:
        text (str): Input text to sanitize
    
    Returns:
        str: Sanitized text
    """
    if not text:
        return ""
    
    # Basic XSS prevention
    text = re.sub(r'<script.*?>.*?</script>', '', text, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r'<.*?>', '', text)
    text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')
    text = text.replace('"', '&quot;')
    text = text.replace("'", '&#x27;')
    
    return text.strip()

def paginate_query(query, page=1, per_page=10):
    """
    Paginate a MongoDB query
    
    Args:
        query: MongoDB query object
        page (int): Page number (1-based)
        per_page (int): Items per page
    
    Returns:
        tuple: (items, total_pages, current_page)
    """
    skip = (page - 1) * per_page
    total_count = query.count()
    total_pages = (total_count + per_page - 1) // per_page
    items = list(query.skip(skip).limit(per_page))
    
    return items, total_pages, page

def login_required(f):
    """
    Decorator to require login for routes
    
    Args:
        f: Function to decorate
    
    Returns:
        Decorated function
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to access this page', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """
    Decorator to require admin access for routes
    
    Args:
        f: Function to decorate
    
    Returns:
        Decorated function
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('user_type') != 'admin':
            flash('Admin access required', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def driver_required(f):
    """
    Decorator to require driver access for routes
    
    Args:
        f: Function to decorate
    
    Returns:
        Decorated function
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('user_type') != 'driver':
            flash('Driver access required', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def generate_api_key():
    """
    Generate a secure API key
    
    Returns:
        str: Generated API key
    """
    import secrets
    return secrets.token_urlsafe(32)

def get_emergency_priority(emergency_type):
    """
    Get priority level for emergency type
    
    Args:
        emergency_type (str): Type of emergency
    
    Returns:
        int: Priority level (1=highest, 5=lowest)
    """
    priority_map = {
        'medical': 1,
        'accident': 2,
        'home': 3,
        'other': 4
    }
    return priority_map.get(emergency_type.lower(), 5)

def format_currency(amount, currency='USD'):
    """
    Format amount as currency
    
    Args:
        amount (float): Amount to format
        currency (str): Currency code
    
    Returns:
        str: Formatted currency string
    """
    return f"${amount:.2f}" if currency == 'USD' else f"{amount:.2f} {currency}"

def calculate_estimated_fare(distance_km, emergency_type='other'):
    """
    Calculate estimated fare based on distance and emergency type
    
    Args:
        distance_km (float): Distance in kilometers
        emergency_type (str): Type of emergency
    
    Returns:
        float: Estimated fare
    """
    base_fare = 5.0  # Base fare
    per_km_rate = 2.0  # Rate per kilometer
    
    # Emergency type multipliers
    emergency_multipliers = {
        'medical': 1.5,
        'accident': 1.3,
        'home': 1.0,
        'other': 1.0
    }
    
    multiplier = emergency_multipliers.get(emergency_type.lower(), 1.0)
    fare = (base_fare + (distance_km * per_km_rate)) * multiplier
    
    return round(fare, 2)

def is_valid_latitude(latitude):
    """
    Validate latitude coordinate
    
    Args:
        latitude (float): Latitude to validate
    
    Returns:
        bool: True if valid, False otherwise
    """
    return -90 <= latitude <= 90

def is_valid_longitude(longitude):
    """
    Validate longitude coordinate
    
    Args:
        longitude (float): Longitude to validate
    
    Returns:
        bool: True if valid, False otherwise
    """
    return -180 <= longitude <= 180

def create_response(success=True, message="", data=None, error_code=None):
    """
    Create standardized API response
    
    Args:
        success (bool): Whether the operation was successful
        message (str): Response message
        data: Response data
        error_code: Error code (if applicable)
    
    Returns:
        dict: Standardized response dictionary
    """
    response = {
        'success': success,
        'message': message,
        'timestamp': datetime.now().isoformat()
    }
    
    if data is not None:
        response['data'] = data
    
    if error_code is not None:
        response['error_code'] = error_code
    
    return response

from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import os
import json
import uuid
from bson import ObjectId
import math
from config_fixed import config as app_config

# Load configuration
app = Flask(__name__)
app.config.from_object(app_config)

# MongoDB connection with connection pooling
client = MongoClient(app.config['MONGODB_URI'], maxPoolSize=50, connectTimeoutMS=30000)
db = client.get_database()

# Collections
users = db.users
drivers = db.drivers
rides = db.rides
emergency_requests = db.emergency_requests

# Helper function to calculate distance between two coordinates
def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371  # Radius of the Earth in kilometers
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2) * math.sin(dlat/2) + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2) * math.sin(dlon/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    distance = R * c
    return distance

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user_type = request.form['user_type']
        
        if user_type == 'user':
            user = users.find_one({'email': email})
            if user and check_password_hash(user['password'], password):
                session['user_id'] = str(user['_id'])
                session['user_type'] = 'user'
                session['user_name'] = user['name']
                return redirect(url_for('user_dashboard'))
        elif user_type == 'driver':
            driver = drivers.find_one({'email': email})
            if driver and check_password_hash(driver['password'], password):
                session['user_id'] = str(driver['_id'])
                session['user_type'] = 'driver'
                session['user_name'] = driver['name']
                return redirect(url_for('driver_dashboard'))
        elif user_type == 'admin':
            if email == 'admin@emergencyride.com' and password == 'admin123':
                session['user_id'] = 'admin'
                session['user_type'] = 'admin'
                session['user_name'] = 'Admin'
                return redirect(url_for('admin_dashboard'))
        
        flash('Invalid credentials', 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        phone = request.form['phone']
        user_type = request.form['user_type']
        
        # Check if user already exists
        if users.find_one({'email': email}) or drivers.find_one({'email': email}):
            flash('Email already registered', 'error')
            return render_template('register.html')
        
        hashed_password = generate_password_hash(password)
        
        if user_type == 'user':
            user_data = {
                'name': name,
                'email': email,
                'password': hashed_password,
                'phone': phone,
                'created_at': datetime.utcnow(),
                'emergency_contacts': []
            }
            users.insert_one(user_data)
        elif user_type == 'driver':
            driver_data = {
                'name': name,
                'email': email,
                'password': hashed_password,
                'phone': phone,
                'license_number': request.form.get('license_number', ''),
                'vehicle_info': {
                    'make': request.form.get('vehicle_make', ''),
                    'model': request.form.get('vehicle_model', ''),
                    'year': request.form.get('vehicle_year', ''),
                    'color': request.form.get('vehicle_color', ''),
                    'plate_number': request.form.get('plate_number', '')
                },
                'is_available': False,
                'current_location': None,
                'rating': 0.0,
                'total_rides': 0,
                'created_at': datetime.utcnow()
            }
            drivers.insert_one(driver_data)
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/user/dashboard')
def user_dashboard():
    if 'user_id' not in session or session['user_type'] != 'user':
        return redirect(url_for('login'))
    
    user = users.find_one({'_id': ObjectId(session['user_id'])})
    recent_rides = list(rides.find({'user_id': ObjectId(session['user_id'])}).sort('created_at', -1).limit(5))
    # Emergency requests for this user
    user_requests_cursor = emergency_requests.find({'user_id': ObjectId(session['user_id'])}).sort('created_at', -1)
    user_requests = list(user_requests_cursor)
    status_counts = {
        'total': len(user_requests),
        'pending': sum(1 for r in user_requests if r.get('status') == 'pending'),
        'in_progress': sum(1 for r in user_requests if r.get('status') == 'in_progress' or r.get('status') == 'accepted'),
        'completed': sum(1 for r in user_requests if r.get('status') == 'completed')
    }
    
    return render_template('user_dashboard.html', user=user, recent_rides=recent_rides, user_requests=user_requests, status_counts=status_counts)

@app.route('/driver/dashboard')
def driver_dashboard():
    if 'user_id' not in session or session['user_type'] != 'driver':
        return redirect(url_for('login'))
    
    driver = drivers.find_one({'_id': ObjectId(session['user_id'])})
    recent_rides = list(rides.find({'driver_id': ObjectId(session['user_id'])}).sort('created_at', -1).limit(5))
    # Emergency requests assigned to this driver
    assigned_requests_cursor = emergency_requests.find({'assigned_driver': ObjectId(session['user_id'])}).sort('created_at', -1)
    assigned_requests = list(assigned_requests_cursor)
    driver_counts = {
        'total': len(assigned_requests),
        'pending': sum(1 for r in assigned_requests if r.get('status') == 'pending'),
        'in_progress': sum(1 for r in assigned_requests if r.get('status') in ['accepted','in_progress']),
        'completed': sum(1 for r in assigned_requests if r.get('status') == 'completed')
    }
    # Unassigned pending requests (available for any driver)
    available_requests_cursor = emergency_requests.find({
        'status': 'pending',
        'assigned_driver': None
    }).sort('created_at', -1)
    available_requests = list(available_requests_cursor)
    
    return render_template('driver_dashboard.html', driver=driver, recent_rides=recent_rides, assigned_requests=assigned_requests, driver_counts=driver_counts, available_requests=available_requests)

@app.route('/driver/requests/<request_id>/accept', methods=['POST'])
def accept_request_driver(request_id):
    if 'user_id' not in session or session['user_type'] != 'driver':
        return redirect(url_for('login'))
    try:
        req_oid = ObjectId(request_id)
    except Exception:
        flash('Invalid request id', 'error')
        return redirect(url_for('driver_dashboard'))
    request_doc = emergency_requests.find_one({'_id': req_oid})
    if not request_doc:
        flash('Request not found', 'error')
        return redirect(url_for('driver_dashboard'))
    # Only accept if not already assigned/completed
    if request_doc.get('status') == 'pending' and not request_doc.get('assigned_driver'):
        emergency_requests.update_one(
            {'_id': req_oid},
            {'$set': {
                'status': 'accepted',
                'assigned_driver': ObjectId(session['user_id']),
                'accepted_at': datetime.utcnow()
            }}
        )
        flash('Request accepted. Proceed to pickup.', 'success')
    else:
        flash('Request is no longer available.', 'error')
    return redirect(url_for('driver_dashboard'))

@app.route('/emergency/request', methods=['GET', 'POST'])
def emergency_request():
    if 'user_id' not in session or session['user_type'] != 'user':
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        data = request.get_json()
        
        emergency_data = {
            'user_id': ObjectId(session['user_id']),
            'pickup_location': {
                'latitude': data['pickup_lat'],
                'longitude': data['pickup_lng'],
                'address': data['pickup_address']
            },
            'destination': {
                'latitude': data['dest_lat'],
                'longitude': data['dest_lng'],
                'address': data['dest_address']
            },
            'emergency_type': data['emergency_type'],
            'description': data.get('description', ''),
            'priority': data.get('priority', 'high'),
            'status': 'pending',
            'created_at': datetime.utcnow(),
            'assigned_driver': None
        }
        
        result = emergency_requests.insert_one(emergency_data)
        
        # Find nearest available drivers
        available_drivers = list(drivers.find({'is_available': True, 'current_location': {'$ne': None}}))
        
        if available_drivers:
            # Calculate distances and find nearest driver
            pickup_lat = data['pickup_lat']
            pickup_lng = data['pickup_lng']
            
            nearest_driver = None
            min_distance = float('inf')
            
            for driver in available_drivers:
                if driver['current_location']:
                    distance = calculate_distance(
                        pickup_lat, pickup_lng,
                        driver['current_location']['latitude'],
                        driver['current_location']['longitude']
                    )
                    if distance < min_distance:
                        min_distance = distance
                        nearest_driver = driver
            
            if nearest_driver:
                # Update emergency request with assigned driver
                emergency_requests.update_one(
                    {'_id': result.inserted_id},
                    {'$set': {'assigned_driver': ObjectId(nearest_driver['_id'])}}
                )
        
        return jsonify({'success': True, 'request_id': str(result.inserted_id)})
    
    return render_template('emergency_request.html')

@app.route('/admin/dashboard')
def admin_dashboard():
    if 'user_id' not in session or session['user_type'] != 'admin':
        return redirect(url_for('login'))
    
    total_users = users.count_documents({})
    total_drivers = drivers.count_documents({})
    total_rides = rides.count_documents({})
    active_emergencies = emergency_requests.count_documents({'status': 'pending'})
    
    recent_emergencies = list(emergency_requests.find().sort('created_at', -1).limit(10))

    # Build maps for quick lookup in template
    user_ids = {e['user_id'] for e in recent_emergencies if e.get('user_id')}
    driver_ids = {e['assigned_driver'] for e in recent_emergencies if e.get('assigned_driver')}
    user_map = {}
    driver_map = {}
    if user_ids:
        for u in users.find({'_id': {'$in': list(user_ids)}}):
            user_map[str(u['_id'])] = u.get('name', 'User')
    if driver_ids:
        for d in drivers.find({'_id': {'$in': list(driver_ids)}}):
            driver_map[str(d['_id'])] = d.get('name', 'Driver')
    
    return render_template('admin_dashboard.html', 
                         total_users=total_users,
                         total_drivers=total_drivers,
                         total_rides=total_rides,
                         active_emergencies=active_emergencies,
                         recent_emergencies=recent_emergencies,
                         user_map=user_map,
                         driver_map=driver_map)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

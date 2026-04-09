from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_socketio import SocketIO, emit, join_room, leave_room
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

# Initialize Socket.IO
socketio = SocketIO(app, cors_allowed_origins="*", async_mode=app.config['SOCKETIO_ASYNC_MODE'], logger=app.debug, engineio_logger=app.debug)

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
            # Allow default hard-coded admin credentials
            if email == 'admin@emergencyride.com' and password == 'admin123':
                session['user_id'] = 'admin'
                session['user_type'] = 'admin'
                session['user_name'] = 'Admin'
                return redirect(url_for('admin_dashboard'))
            # Or validate against DB if admin user exists
            admin_user = users.find_one({'email': email, 'role': 'admin'})
            if admin_user and check_password_hash(admin_user['password'], password):
                session['user_id'] = str(admin_user['_id'])
                session['user_type'] = 'admin'
                session['user_name'] = admin_user.get('name', 'Admin')
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
    
    return render_template('user_dashboard.html', user=user, recent_rides=recent_rides)

@app.route('/driver/dashboard')
def driver_dashboard():
    if 'user_id' not in session or session['user_type'] != 'driver':
        return redirect(url_for('login'))
    
    driver = drivers.find_one({'_id': ObjectId(session['user_id'])})
    recent_rides = list(rides.find({'driver_id': ObjectId(session['user_id'])}).sort('created_at', -1).limit(5))
    
    return render_template('driver_dashboard.html', driver=driver, recent_rides=recent_rides)

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
        
        # Notify admin about new emergency request
        socketio.emit('new_emergency_request', {
            'request_id': str(result.inserted_id),
            'user_id': str(emergency_data['user_id']),
            'user_name': session['user_name'],
            'emergency_type': emergency_data['emergency_type'],
            'pickup_location': emergency_data['pickup_location'],
            'destination': emergency_data['destination'],
            'priority': emergency_data['priority'],
            'created_at': emergency_data['created_at'].isoformat()
        }, room="admin_room")
        
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
                
                # Emit to specific driver
                socketio.emit('emergency_request', {
                    'request_id': str(result.inserted_id),
                    'pickup_location': emergency_data['pickup_location'],
                    'destination': emergency_data['destination'],
                    'emergency_type': emergency_data['emergency_type'],
                    'description': emergency_data['description'],
                    'user_name': session['user_name'],
                    'priority': emergency_data['priority'],
                    'distance': round(min_distance, 2)
                }, room=f"driver_{nearest_driver['_id']}")
                
                # Also emit to all drivers for backup
                socketio.emit('emergency_request_broadcast', {
                    'request_id': str(result.inserted_id),
                    'pickup_location': emergency_data['pickup_location'],
                    'destination': emergency_data['destination'],
                    'emergency_type': emergency_data['emergency_type'],
                    'description': emergency_data['description'],
                    'user_name': session['user_name'],
                    'priority': emergency_data['priority'],
                    'assigned_driver': str(nearest_driver['_id'])
                }, room="all_drivers")
        else:
            # No drivers available - notify user and admin
            socketio.emit('no_drivers_available', {
                'request_id': str(result.inserted_id),
                'message': 'No drivers are currently available. Your request has been queued.'
            }, room=f"user_{session['user_id']}")
            
            socketio.emit('no_drivers_available_admin', {
                'request_id': str(result.inserted_id),
                'user_name': session['user_name'],
                'emergency_type': emergency_data['emergency_type']
            }, room="admin_room")
        
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
    
    return render_template('admin_dashboard.html', 
                         total_users=total_users,
                         total_drivers=total_drivers,
                         total_rides=total_rides,
                         active_emergencies=active_emergencies,
                         recent_emergencies=recent_emergencies)

# Socket.IO events
@socketio.on('connect')
def handle_connect():
    print(f"Client connected: {request.sid}")
    if 'user_id' in session:
        user_id = session['user_id']
        user_type = session['user_type']
        
        if user_type == 'driver':
            join_room(f"driver_{user_id}")
            join_room("all_drivers")
            # Update driver status to online
            drivers.update_one(
                {'_id': ObjectId(user_id)},
                {'$set': {'is_online': True}}
            )
            print(f"Driver {user_id} joined room")
        elif user_type == 'user':
            join_room(f"user_{user_id}")
            print(f"User {user_id} joined room")
        elif user_type == 'admin':
            join_room("admin_room")
            print(f"Admin {user_id} joined room")
        
        # Notify admin about user connection
        socketio.emit('user_connected', {
            'user_id': user_id,
            'user_type': user_type,
            'user_name': session.get('user_name', 'Unknown')
        }, room="admin_room")

@socketio.on('disconnect')
def handle_disconnect():
    print(f"Client disconnected: {request.sid}")
    if 'user_id' in session:
        user_id = session['user_id']
        user_type = session['user_type']
        
        if user_type == 'driver':
            leave_room(f"driver_{user_id}")
            leave_room("all_drivers")
            # Update driver status to offline
            drivers.update_one(
                {'_id': ObjectId(user_id)},
                {'$set': {'is_online': False, 'is_available': False}}
            )
        elif user_type == 'user':
            leave_room(f"user_{user_id}")
        elif user_type == 'admin':
            leave_room("admin_room")
        
        # Notify admin about user disconnection
        socketio.emit('user_disconnected', {
            'user_id': user_id,
            'user_type': user_type,
            'user_name': session.get('user_name', 'Unknown')
        }, room="admin_room")

@socketio.on('driver_location_update')
def handle_driver_location(data):
    if 'user_id' in session and session['user_type'] == 'driver':
        drivers.update_one(
            {'_id': ObjectId(session['user_id'])},
            {'$set': {'current_location': {
                'latitude': data['latitude'],
                'longitude': data['longitude']
            }}}
        )

@socketio.on('driver_availability')
def handle_driver_availability(data):
    if 'user_id' in session and session['user_type'] == 'driver':
        drivers.update_one(
            {'_id': ObjectId(session['user_id'])},
            {'$set': {'is_available': data['available']}}
        )

@socketio.on('accept_emergency_request')
def handle_accept_request(data):
    if 'user_id' in session and session['user_type'] == 'driver':
        request_id = data['request_id']
        
        # Update emergency request
        emergency_requests.update_one(
            {'_id': ObjectId(request_id)},
            {'$set': {
                'status': 'accepted',
                'assigned_driver': ObjectId(session['user_id']),
                'accepted_at': datetime.utcnow()
            }}
        )
        
        # Get request details
        request_data = emergency_requests.find_one({'_id': ObjectId(request_id)})
        user_id = request_data['user_id']
        
        # Get driver details
        driver = drivers.find_one({'_id': ObjectId(session['user_id'])})
        
        # Notify user
        socketio.emit('request_accepted', {
            'request_id': request_id,
            'driver_name': session['user_name'],
            'driver_phone': driver.get('phone', ''),
            'vehicle_info': driver.get('vehicle_info', {}),
            'estimated_arrival': '5-10 minutes'
        }, room=f"user_{user_id}")
        
        # Notify admin
        socketio.emit('request_accepted_admin', {
            'request_id': request_id,
            'user_name': request_data.get('user_name', 'Unknown'),
            'driver_name': session['user_name'],
            'emergency_type': request_data['emergency_type'],
            'accepted_at': datetime.utcnow().isoformat()
        }, room="admin_room")
        
        # Notify other drivers that request was taken
        socketio.emit('request_taken', {
            'request_id': request_id,
            'taken_by': session['user_name']
        }, room="all_drivers")

@socketio.on('reject_emergency_request')
def handle_reject_request(data):
    if 'user_id' in session and session['user_type'] == 'driver':
        request_id = data['request_id']
        reason = data.get('reason', 'No reason provided')
        
        # Get request details
        request_data = emergency_requests.find_one({'_id': ObjectId(request_id)})
        if request_data:
            user_id = request_data['user_id']
            
            # Notify user
            socketio.emit('request_rejected', {
                'request_id': request_id,
                'driver_name': session['user_name'],
                'reason': reason,
                'message': 'Your request was rejected. We are finding another driver.'
            }, room=f"user_{user_id}")
            
            # Notify admin
            socketio.emit('request_rejected_admin', {
                'request_id': request_id,
                'user_name': request_data.get('user_name', 'Unknown'),
                'driver_name': session['user_name'],
                'reason': reason,
                'rejected_at': datetime.utcnow().isoformat()
            }, room="admin_room")
            
            # Try to find another available driver
            available_drivers = list(drivers.find({
                'is_available': True, 
                'current_location': {'$ne': None},
                '_id': {'$ne': ObjectId(session['user_id'])}
            }))
            
            if available_drivers and request_data['pickup_location']:
                pickup_lat = request_data['pickup_location']['latitude']
                pickup_lng = request_data['pickup_location']['longitude']
                
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
                    # Update emergency request with new assigned driver
                    emergency_requests.update_one(
                        {'_id': ObjectId(request_id)},
                        {'$set': {'assigned_driver': ObjectId(nearest_driver['_id'])}}
                    )
                    
                    # Emit to new driver
                    socketio.emit('emergency_request', {
                        'request_id': request_id,
                        'pickup_location': request_data['pickup_location'],
                        'destination': request_data['destination'],
                        'emergency_type': request_data['emergency_type'],
                        'description': request_data['description'],
                        'user_name': request_data.get('user_name', 'Unknown'),
                        'priority': request_data.get('priority', 'high'),
                        'distance': round(min_distance, 2)
                    }, room=f"driver_{nearest_driver['_id']}")

@socketio.on('ride_started')
def handle_ride_started(data):
    if 'user_id' in session and session['user_type'] == 'driver':
        request_id = data['request_id']
        
        # Create ride record
        request_data = emergency_requests.find_one({'_id': ObjectId(request_id)})
        
        ride_data = {
            'user_id': request_data['user_id'],
            'driver_id': ObjectId(session['user_id']),
            'pickup_location': request_data['pickup_location'],
            'destination': request_data['destination'],
            'emergency_type': request_data['emergency_type'],
            'status': 'in_progress',
            'started_at': datetime.utcnow(),
            'completed_at': None,
            'rating': None
        }
        
        rides.insert_one(ride_data)
        
        # Update emergency request
        emergency_requests.update_one(
            {'_id': ObjectId(request_id)},
            {'$set': {'status': 'in_progress'}}
        )
        
        # Notify user
        socketio.emit('ride_started', {
            'request_id': request_id,
            'driver_name': session['user_name']
        }, room=f"user_{request_data['user_id']}")

@socketio.on('ride_completed')
def handle_ride_completed(data):
    if 'user_id' in session and session['user_type'] == 'driver':
        request_id = data['request_id']
        rating = data.get('rating', 5)
        
        # Update ride record
        rides.update_one(
            {'user_id': ObjectId(session['user_id'])},
            {'$set': {
                'status': 'completed',
                'completed_at': datetime.utcnow(),
                'rating': rating
            }}
        )
        
        # Update emergency request
        emergency_requests.update_one(
            {'_id': ObjectId(request_id)},
            {'$set': {'status': 'completed'}}
        )
        
        # Update driver stats
        drivers.update_one(
            {'_id': ObjectId(session['user_id'])},
            {'$inc': {'total_rides': 1}}
        )
        
        # Notify user
        request_data = emergency_requests.find_one({'_id': ObjectId(request_id)})
        socketio.emit('ride_completed', {
            'request_id': request_id
        }, room=f"user_{request_data['user_id']}")

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)

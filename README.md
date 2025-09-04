# Emergency Ride-Hailing Application

A web-based Emergency Ride-Hailing Application designed to provide immediate transportation assistance during emergency situations. This application connects users with the nearest available drivers in real-time for swift emergency response.

## Default Admin Credentials

- Email: admin@emergencyride.com
- Password: admin123

These are for development and demo only. For production, remove hard-coded credentials, create a real admin account in MongoDB, and set strong secrets via environment variables.

## Features

### Core Functionality
- **User Authentication**: Secure login and registration for users, drivers, and administrators
- **Real-time Geolocation**: GPS tracking and location-based driver matching
- **Emergency Request System**: Quick emergency ride requests with priority levels
- **Driver Management**: Driver availability, location tracking, and ride acceptance
- **Real-time Communication**: Instant notifications using Socket.IO
- **Admin Dashboard**: System monitoring and management capabilities

### Emergency Types Supported
- Medical Emergency
- Home Emergency
- Accident
- Other Emergency Situations

### User Roles
1. **Users**: Can request emergency rides and track their requests
2. **Drivers**: Can accept emergency requests and manage rides
3. **Administrators**: Can monitor system activity and manage users/drivers

## Technology Stack

- **Backend**: Flask (Python)
- **Database**: MongoDB
- **Frontend**: HTML Templates with Bootstrap 5
- **Real-time Communication**: Socket.IO
- **Maps Integration**: OpenStreetMap via Leaflet (no API key required)
- **Styling**: Custom CSS with Bootstrap

## Installation

### Prerequisites
- Python 3.8 or higher
- MongoDB (local or cloud instance)

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd emergency-ride-hailing
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application (simple, without sockets)**
   ```bash
   python app_simple.py
   ```

5. **Access the application**
   - Open your browser and go to `http://localhost:5000`

## Project Structure

```
emergency-ride-hailing/
├── app.py                 # Main Flask application with sockets (requires compatible async env)
├── app_simple.py          # Simpler Flask app without sockets (recommended for quick start)
├── requirements.txt       # Python dependencies
├── README.md             # Project documentation
├── static/               # Static files
│   ├── css/
│   │   └── style.css     # Custom styles
│   └── images/           # Images and assets
├── templates/            # HTML templates
│   ├── base.html         # Base template (Leaflet included)
│   ├── index.html        # Home page
│   ├── login.html        # Login page
│   ├── register.html     # Registration page
│   ├── user_dashboard.html      # User dashboard
│   ├── driver_dashboard.html    # Driver dashboard (available/assigned requests)
│   ├── emergency_request.html   # Emergency request form (Leaflet + Nominatim)
│   └── admin_dashboard.html     # Admin dashboard
└── PROJECT_SUMMARY.md
```

## Security Considerations

- Hard-coded admin credentials are for development only; remove before production
- Passwords are hashed using Werkzeug
- Session management for user authentication
- Input validation and sanitization

## Future Enhancements

- Bring back real-time updates with Socket.IO using a Python version compatible with async drivers
- Add autocomplete for addresses using Photon/Nominatim
- Payment integration, reports and analytics, push notifications

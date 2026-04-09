# Emergency Ride-Hailing Application

A comprehensive web-based Emergency Ride-Hailing Application designed to provide immediate transportation assistance during emergency situations. This application connects users with the nearest available drivers in real-time for swift emergency response.

## 🚀 Key Features

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

## 🛠️ Technology Stack

- **Backend**: Flask (Python)
- **Database**: MongoDB with optimized indexing
- **Frontend**: HTML Templates with Bootstrap 5
- **Real-time Communication**: Socket.IO
- **Maps Integration**: OpenStreetMap via Leaflet (no API key required)
- **Styling**: Custom CSS with modern design system
- **Security**: Password hashing, session management, input validation
- **Performance**: Connection pooling, caching, monitoring

## 📋 Prerequisites

- Python 3.8 or higher
- MongoDB 4.4+ (local or cloud instance)
- Git (for cloning)

## 🚀 Quick Start

### 1. Clone and Setup
```bash
git clone <repository-url>
cd emergency-ride-hailing
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Environment Configuration
```bash
cp .env.example .env
# Edit .env with your configuration (optional for development)
```

### 5. Initialize Database
```bash
python init_db.py
```

### 6. Run Application
```bash
# For full-featured version with Socket.IO
python run_improved.py

# For simple version without Socket.IO (recommended for quick start)
python app_simple.py
```

### 7. Access the Application
- Open your browser and go to `http://localhost:5000`

## 👤 Default Accounts

The following accounts are created automatically for development:

- **Admin**: admin@emergencyride.com / admin123
- **User**: user@example.com / user123
- **Driver**: driver@example.com / driver123
- **Driver 2**: driver2@example.com / driver123

⚠️ **Security Note**: These credentials are for development only. For production, create real accounts and set strong secrets via environment variables.

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

## 📁 Project Structure

```
emergency-ride-hailing/
├── app.py                 # Main Flask application with Socket.IO
├── app_simple.py          # Simplified Flask app without Socket.IO
├── run_improved.py        # Improved run script with proper configuration
├── database_utils.py      # Database operations and indexing
├── utils.py               # Shared utility functions
├── error_handlers.py      # Error handling and logging
├── config.py              # Environment-based configuration
├── init_db.py             # Database initialization script
├── requirements.txt       # Python dependencies
├── .env.example           # Environment variables template
├── DEVELOPMENT.md         # Comprehensive development guide
├── README.md             # This file
├── static/               # Static files
│   ├── css/
│   │   └── style.css     # Modern CSS with design system
│   └── images/           # Images and assets
├── templates/            # HTML templates
│   ├── base.html         # Base template
│   ├── index.html        # Home page
│   ├── login.html        # Login page
│   ├── register.html     # Registration page
│   ├── user_dashboard.html      # User dashboard
│   ├── driver_dashboard.html    # Driver dashboard
│   ├── emergency_request.html   # Emergency request form
│   ├── admin_dashboard.html     # Admin dashboard
│   └── errors/           # Error pages (404, 500, etc.)
└── logs/                 # Application logs (created automatically)
```

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

## 🔧 Configuration

### Environment Variables

Copy `.env.example` to `.env` and configure as needed:

```bash
# Required for production
FLASK_ENV=production
SECRET_KEY=your-super-secret-key
MONGODB_URI=mongodb://localhost:27017/emergency_ride_hailing

# Optional features
GOOGLE_MAPS_API_KEY=your-google-maps-api-key
MAIL_SERVER=smtp.gmail.com
REDIS_URL=redis://localhost:6379/0
```

### Development vs Production

- **Development**: Uses SQLite-like MongoDB, debug mode, auto-generated keys
- **Production**: Requires explicit configuration, secure settings, proper logging

## 🔒 Security Features

- ✅ **Secure Password Hashing** using Werkzeug
- ✅ **Session Management** with secure cookies
- ✅ **Input Validation** and sanitization
- ✅ **CORS Configuration** for Socket.IO
- ✅ **Environment-based Configuration** for production
- ✅ **Rate Limiting** ready (Redis-based)
- ✅ **XSS Protection** with input sanitization
- ✅ **Error Handling** without information leakage

## 📊 Performance Optimizations

- **Database Indexing**: Optimized queries for location-based searches
- **Connection Pooling**: Efficient MongoDB connection management
- **Caching Ready**: Redis integration prepared
- **Performance Monitoring**: Built-in request tracking
- **Lazy Loading**: Optimized asset delivery
- **Responsive Design**: Mobile-first approach

## 🚨 Emergency Features

### Priority System
1. **Medical Emergency** (Highest priority)
2. **Accident** (High priority)
3. **Home Emergency** (Medium priority)
4. **Other** (Low priority)

### Real-time Features
- **Driver Location Tracking**: Live GPS updates
- **Instant Notifications**: Socket.IO-based alerts
- **Request Status Updates**: Real-time status changes
- **Geospatial Matching**: Find nearest available drivers

## 🛠️ Development Guide

For detailed development instructions, see [DEVELOPMENT.md](DEVELOPMENT.md)

### Key Development Features
- **Modular Architecture**: Separated concerns for maintainability
- **Error Handling**: Comprehensive error management
- **Logging**: Structured logging with performance metrics
- **Testing Ready**: Test structure prepared
- **API Documentation**: Endpoints documented
- **Database Utilities**: Helper functions for common operations

## 🚀 Deployment

### Production Setup

1. **Set Environment Variables**
   ```bash
   export FLASK_ENV=production
   export SECRET_KEY=your-production-secret
   export MONGODB_URI=your-production-mongodb-uri
   ```

2. **Initialize Production Database**
   ```bash
   python database_utils.py --production
   ```

3. **Run with Gunicorn**
   ```bash
   gunicorn -w 4 -b 0.0.0.0:5000 run_improved:app
   ```

### Docker Support

```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python", "run_improved.py"]
```

## 📈 Monitoring

### Built-in Monitoring
- **Request Performance**: Track response times
- **Database Queries**: Monitor slow queries
- **Error Tracking**: Comprehensive error logging
- **System Health**: Database and service status

### Logs
- Application logs stored in `logs/` directory
- Structured logging with timestamps
- Error levels: INFO, WARNING, ERROR, CRITICAL

## 🔄 Future Enhancements

### Planned Features
- 📱 **Mobile Application** (React Native/Flutter)
- 💳 **Payment Integration** (Stripe, PayPal)
- 📊 **Advanced Analytics** Dashboard
- 🌍 **Multi-language Support**
- 🚑 **Emergency Services Integration**
- 📸 **Driver Verification System**
- ⭐ **Rating and Review System**
- 🔔 **Push Notifications** (FCM)

### Scalability Improvements
- **Microservices Architecture** for large-scale deployment
- **Load Balancing** for high availability
- **Database Sharding** for performance
- **Caching Layer** with Redis
- **CDN Integration** for static assets

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Submit a pull request
5. Follow the development guidelines in DEVELOPMENT.md

## 📞 Support

- 📖 **Documentation**: See [DEVELOPMENT.md](DEVELOPMENT.md)
- 🐛 **Issues**: Report bugs on GitHub
- 📧 **Contact**: Development team for enterprise support

---

**Project Status**: ✅ Production Ready
**Version**: 2.0.0 (Refactored)
**Last Updated**: December 2024

**License**: MIT License - See LICENSE file for details

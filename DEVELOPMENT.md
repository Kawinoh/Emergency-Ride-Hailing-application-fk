# Development Guide - Emergency Ride-Hailing Application

## Overview

This document provides comprehensive development guidelines for the Emergency Ride-Hailing Application. The application has been refactored with improved security, performance, and maintainability.

## Architecture

### Core Components

- **Flask Application** (`app.py`, `app_simple.py`) - Main web application
- **Database Utilities** (`database_utils.py`) - Database operations and indexing
- **Configuration** (`config.py`) - Environment-based configuration
- **Error Handling** (`error_handlers.py`) - Centralized error handling and logging
- **Utilities** (`utils.py`) - Shared helper functions and decorators
- **Templates** (`templates/`) - HTML templates with modern UI
- **Static Assets** (`static/`) - CSS, JavaScript, and images

### Database Schema

#### Collections
1. **users** - User accounts and profiles
2. **drivers** - Driver accounts and vehicle information
3. **emergency_requests** - Emergency ride requests
4. **rides** - Completed ride records

#### Indexes
- Email uniqueness indexes
- Geospatial indexes for location queries
- Compound indexes for performance
- Status-based indexes for filtering

## Setup Instructions

### Prerequisites
- Python 3.8+
- MongoDB 4.4+
- Node.js (for asset building, optional)

### Quick Start

1. **Clone and Setup**
   ```bash
   git clone <repository-url>
   cd emergency-ride-hailing
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Configuration**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Initialize Database**
   ```bash
   python init_db.py
   ```

6. **Run Application**
   ```bash
   # For development with Socket.IO
   python run_improved.py
   
   # For simple version without Socket.IO
   python app_simple.py
   ```

## Development Guidelines

### Code Organization

1. **Use the utilities module** for common functions
2. **Follow the configuration pattern** for environment-specific settings
3. **Implement proper error handling** using decorators
4. **Use the database manager** for all database operations

### Security Best Practices

1. **Never hard-code credentials** - use environment variables
2. **Validate all inputs** using utility functions
3. **Use proper authentication** decorators
4. **Implement rate limiting** for API endpoints
5. **Sanitize user inputs** to prevent XSS

### Performance Optimization

1. **Use database indexes** for frequently queried fields
2. **Implement connection pooling** for MongoDB
3. **Cache frequently accessed data**
4. **Monitor slow queries** using performance monitoring
5. **Use pagination** for large datasets

### Testing

1. **Unit tests** for utility functions
2. **Integration tests** for database operations
3. **API tests** for endpoints
4. **UI tests** for user workflows

## API Documentation

### Authentication Endpoints

- `POST /login` - User authentication
- `POST /register` - User registration
- `GET /logout` - User logout

### Emergency Request Endpoints

- `POST /emergency/request` - Create emergency request
- `GET /emergency/status/<request_id>` - Get request status
- `PUT /emergency/cancel/<request_id>` - Cancel request

### Driver Endpoints

- `GET /driver/dashboard` - Driver dashboard
- `POST /driver/location/update` - Update driver location
- `POST /driver/accept/<request_id>` - Accept emergency request

### Admin Endpoints

- `GET /admin/dashboard` - Admin dashboard
- `GET /admin/users` - Manage users
- `GET /admin/drivers` - Manage drivers
- `GET /admin/analytics` - System analytics

## Configuration

### Environment Variables

```bash
# Required
FLASK_ENV=development
SECRET_KEY=your-secret-key
MONGODB_URI=mongodb://localhost:27017/emergency_ride_hailing

# Optional
GOOGLE_MAPS_API_KEY=your-api-key
MAIL_SERVER=smtp.gmail.com
REDIS_URL=redis://localhost:6379/0
```

### Configuration Classes

- **DevelopmentConfig** - Development environment settings
- **ProductionConfig** - Production environment settings
- **TestingConfig** - Testing environment settings

## Database Management

### Creating Indexes

```python
from database_utils import DatabaseManager

db_manager = DatabaseManager('development')
db_manager.create_indexes()
```

### Finding Nearest Drivers

```python
drivers = db_manager.find_nearest_drivers(
    latitude=40.7128,
    longitude=-74.0060,
    max_distance_km=10,
    limit=5
)
```

### Performance Monitoring

```python
from error_handlers import performance_monitor

stats = performance_monitor.get_performance_stats()
```

## Error Handling

### Custom Exceptions

- `DatabaseError` - Database operation errors
- `AuthenticationError` - Authentication failures
- `ValidationError` - Input validation errors
- `EmergencyError` - Emergency-specific errors

### Logging

```python
from error_handlers import log_error

log_error('CustomError', 'Error message', {'details': 'error details'})
```

## Frontend Development

### CSS Architecture

- **CSS Variables** for theming
- **Component-based** styling
- **Responsive design** with mobile-first approach
- **Modern animations** and transitions

### JavaScript Features

- **Real-time updates** with Socket.IO
- **Geolocation** services
- **Map integration** with Leaflet
- **Form validation** and error handling

## Deployment

### Production Setup

1. **Environment Configuration**
   ```bash
   export FLASK_ENV=production
   export SECRET_KEY=your-production-secret
   export MONGODB_URI=your-production-mongodb-uri
   ```

2. **Database Setup**
   ```bash
   python database_utils.py --production
   ```

3. **Run Application**
   ```bash
   gunicorn -w 4 -b 0.0.0.0:5000 run_improved:app
   ```

### Docker Deployment

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5000

CMD ["python", "run_improved.py"]
```

## Monitoring and Maintenance

### Health Checks

- Database connectivity
- Redis connection (if used)
- External API status
- System resources

### Backup Strategy

- Daily database backups
- Configuration file backups
- Log rotation and archival

### Performance Metrics

- Response times
- Database query performance
- Memory usage
- Error rates

## Contributing

### Code Style

- Follow PEP 8 guidelines
- Use meaningful variable names
- Add docstrings to functions
- Include type hints where appropriate

### Git Workflow

1. Create feature branch
2. Make changes with tests
3. Submit pull request
4. Code review and merge

### Code Review Checklist

- [ ] Security considerations
- [ ] Performance impact
- [ ] Error handling
- [ ] Documentation
- [ ] Test coverage

## Troubleshooting

### Common Issues

1. **MongoDB Connection Failed**
   - Check MongoDB service status
   - Verify connection string
   - Check network connectivity

2. **Socket.IO Not Working**
   - Verify async mode configuration
   - Check CORS settings
   - Ensure compatible Python version

3. **Performance Issues**
   - Check database indexes
   - Monitor slow queries
   - Review connection pooling

### Debug Mode

```bash
export FLASK_ENV=development
export FLASK_DEBUG=True
python run_improved.py
```

## Security Considerations

### Input Validation

- Email validation
- Phone number validation
- Password strength requirements
- Coordinate validation

### Authentication & Authorization

- Session management
- Role-based access control
- API key management
- Rate limiting

### Data Protection

- Password hashing
- Input sanitization
- HTTPS enforcement
- Secure headers

## Future Enhancements

### Planned Features

- Mobile application development
- Payment integration
- Advanced analytics dashboard
- Multi-language support
- Integration with emergency services

### Scalability Improvements

- Microservices architecture
- Load balancing
- Database sharding
- Caching layer
- CDN integration

## Support

For development support:
1. Check this documentation
2. Review error logs
3. Check GitHub issues
4. Contact development team

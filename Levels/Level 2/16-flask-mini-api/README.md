# Flask Mini API

A simple REST API built with Flask for managing tasks and users. This project demonstrates intermediate Python development skills including API design, database integration, authentication, and comprehensive testing.

## Features

### Required Features ✅

- **Flask REST API**: Complete CRUD operations for tasks and users
- **In-memory data store**: Fallback storage with SQLite persistence
- **JSON request/response handling**: Full JSON API with proper content types
- **Basic error handling**: 400, 404, and 500 error responses
- **Input validation**: Comprehensive data validation with schemas

### Bonus Features ✅

- **SQLite persistence**: Database storage with automatic fallback to in-memory
- **Authentication with API keys**: Secure API key-based authentication
- **Swagger/OpenAPI documentation**: Available at `/docs` endpoint

## Installation

### Prerequisites

- Python 3.8 or higher
- pip for package management
- Virtual environment (recommended)

### Setup

1. **Clone or download the project**
   ```bash
   cd 16-flask-mini-api
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python -m flask_mini_api.main
   ```

The API will be available at `http://localhost:5000`

## Usage

### Authentication

All API endpoints (except health check and auth endpoints) require authentication via API key.

#### Register a new user
```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "email": "test@example.com"}'
```

#### Login to get API key
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser"}'
```

### API Endpoints

#### Health Check
```bash
curl http://localhost:5000/health
```

#### Tasks

**Get all tasks**
```bash
curl -X GET http://localhost:5000/api/tasks \
  -H "X-API-Key: your_api_key_here"
```

**Get specific task**
```bash
curl -X GET http://localhost:5000/api/tasks/1 \
  -H "X-API-Key: your_api_key_here"
```

**Create task**
```bash
curl -X POST http://localhost:5000/api/tasks \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your_api_key_here" \
  -d '{
    "title": "Learn Flask",
    "description": "Build a REST API with Flask",
    "priority": "high",
    "completed": false
  }'
```

**Update task**
```bash
curl -X PUT http://localhost:5000/api/tasks/1 \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your_api_key_here" \
  -d '{"completed": true}'
```

**Delete task**
```bash
curl -X DELETE http://localhost:5000/api/tasks/1 \
  -H "X-API-Key: your_api_key_here"
```

#### Users

**Get all users**
```bash
curl -X GET http://localhost:5000/api/users \
  -H "X-API-Key: your_api_key_here"
```

**Get specific user**
```bash
curl -X GET http://localhost:5000/api/users/1 \
  -H "X-API-Key: your_api_key_here"
```

**Create user**
```bash
curl -X POST http://localhost:5000/api/users \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your_api_key_here" \
  -d '{
    "username": "newuser",
    "email": "newuser@example.com"
  }'
```

**Update user**
```bash
curl -X PUT http://localhost:5000/api/users/1 \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your_api_key_here" \
  -d '{"email": "updated@example.com"}'
```

**Delete user**
```bash
curl -X DELETE http://localhost:5000/api/users/1 \
  -H "X-API-Key: your_api_key_here"
```

## Configuration

### Environment Variables

The application can be configured using environment variables:

- `FLASK_ENV`: Set to `development` or `production`
- `SECRET_KEY`: Secret key for Flask sessions
- `DATABASE_URL`: Database connection string

### Database

The application uses SQLite by default with automatic fallback to in-memory storage. The database file (`flask_mini_api.db`) is created automatically on first run.

## API Documentation

### Response Format

All API responses follow a consistent format:

**Success Response**
```json
{
  "success": true,
  "data": {...},
  "message": "Optional success message"
}
```

**Error Response**
```json
{
  "success": false,
  "error": "Error type",
  "message": "Error description",
  "status_code": 400
}
```

### Data Models

#### Task
```json
{
  "id": 1,
  "title": "Task title",
  "description": "Task description",
  "completed": false,
  "priority": "medium",
  "created_at": "2023-01-01T00:00:00",
  "updated_at": "2023-01-01T00:00:00"
}
```

#### User
```json
{
  "id": 1,
  "username": "username",
  "email": "user@example.com",
  "api_key": "generated_api_key",
  "created_at": "2023-01-01T00:00:00",
  "updated_at": "2023-01-01T00:00:00"
}
```

### Validation Rules

#### Task Validation
- `title`: Required, string, max 200 characters
- `description`: Optional, string, max 1000 characters
- `completed`: Optional, boolean
- `priority`: Optional, one of: "low", "medium", "high"

#### User Validation
- `username`: Required, string, 3-50 characters, alphanumeric + underscore only
- `email`: Required, string, valid email format, max 100 characters
- `api_key`: Auto-generated, 32 characters

## Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=flask_mini_api

# Run specific test file
pytest tests/test_flask_mini_api.py

# Run with verbose output
pytest -v
```

### Test Coverage

The test suite includes:
- Unit tests for all API endpoints
- Authentication and authorization tests
- Data validation tests
- Error handling tests
- Core business logic tests

## Project Structure

```
16-flask-mini-api/
├── flask_mini_api/          # Main package
│   ├── __init__.py         # Package initialization
│   ├── main.py             # Flask app and routes
│   ├── core.py             # Business logic classes
│   ├── utils.py            # Utility functions
│   └── auth.py             # Authentication module
├── tests/                  # Test suite
│   ├── __init__.py
│   └── test_flask_mini_api.py
├── requirements.txt        # Dependencies
├── README.md              # This file
├── CHECKLIST.md           # Feature checklist
└── SPEC.md               # Project specification
```

## Development

### Code Quality

The project follows Python best practices:

- **Type hints**: All public functions have type annotations
- **Docstrings**: Comprehensive documentation for all modules and functions
- **Error handling**: Proper exception handling with meaningful error messages
- **Logging**: Structured logging for debugging and monitoring
- **Code formatting**: Code formatted with `black` and linted with `ruff`

### Adding New Features

1. Add new routes to `main.py`
2. Implement business logic in `core.py`
3. Add validation in `utils.py`
4. Write tests in `tests/`
5. Update documentation

## Known Limitations

- **Single database**: Currently supports only SQLite
- **No pagination**: Large datasets may impact performance
- **Basic authentication**: No password-based auth or JWT tokens
- **No rate limiting**: API calls are not rate limited
- **No caching**: No caching layer for improved performance

## Troubleshooting

### Common Issues

1. **Database errors**: Check file permissions for database file
2. **Import errors**: Ensure virtual environment is activated
3. **Port conflicts**: Change port in `main.py` if 5000 is occupied
4. **Authentication failures**: Verify API key format and user existence

### Debug Mode

Run with debug mode for detailed error messages:

```python
app.run(debug=True)
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## License

This project is for educational purposes. Feel free to use and modify as needed.

## Changelog

### Version 1.0.0
- Initial release
- Complete CRUD operations for tasks and users
- API key authentication
- SQLite persistence with in-memory fallback
- Comprehensive test suite
- Full documentation

# Architecture Documentation

## Overview

The Flask CRUD To-Do application follows a clean, layered architecture pattern that separates concerns and promotes maintainability. The architecture is designed to be scalable, testable, and follows Flask best practices.

## Architecture Layers

### 1. Presentation Layer (Routes)

**Location**: `app/routes/`

The presentation layer handles HTTP requests and responses. It's organized into blueprints:

- **`auth.py`**: Authentication routes (register, login, logout)
- **`tasks.py`**: Task CRUD routes with filtering, sorting, pagination
- **`main.py`**: Main routes and error handlers

**Responsibilities**:
- Parse HTTP requests
- Validate input data
- Call service layer methods
- Format responses (HTML templates or JSON)
- Handle errors and flash messages

**Design Decisions**:
- Uses Flask blueprints for modular organization
- Routes are thin - business logic is in services
- Flash messages for user feedback
- Custom error handlers for 404 and 500 errors

### 2. Business Logic Layer (Services)

**Location**: `app/services/`

The service layer contains business logic and orchestrates data operations:

- **`auth_service.py`**: User registration and authentication
- **`task_service.py`**: Task CRUD operations, filtering, sorting, pagination

**Responsibilities**:
- Implement business rules
- Coordinate database operations
- Handle business-level exceptions
- Provide clean interfaces for routes

**Design Decisions**:
- Services are stateless
- All database operations go through services
- Services raise custom exceptions for error handling
- Logging is done at the service layer

### 3. Data Access Layer (Models)

**Location**: `app/models/`

The data layer defines database models and relationships:

- **`user.py`**: User model with password hashing
- **`task.py`**: Task model with relationships

**Responsibilities**:
- Define database schema
- Handle data validation at model level
- Manage relationships between entities
- Provide model-level methods

**Design Decisions**:
- Uses SQLAlchemy ORM for database abstraction
- Models include helper methods (e.g., `set_password`, `toggle_completed`)
- Relationships are defined for efficient querying
- Indexes on frequently queried fields

### 4. Utilities Layer

**Location**: `app/utils/`

Utility functions and shared code:

- **`exceptions.py`**: Custom exception classes
- **`decorators.py`**: Custom decorators (e.g., `login_required`)

**Design Decisions**:
- Custom exceptions for better error handling
- Reusable decorators for common patterns

## Database Design

### Schema

**Users Table**:
- `id` (Primary Key)
- `username` (Unique, Indexed)
- `email` (Unique, Indexed)
- `password_hash` (Hashed password)
- `created_at` (Timestamp)

**Tasks Table**:
- `id` (Primary Key)
- `title` (Required)
- `description` (Optional)
- `completed` (Boolean, Indexed)
- `created_at` (Timestamp, Indexed)
- `updated_at` (Timestamp)
- `user_id` (Foreign Key to Users, Indexed)

### Relationships

- **User → Tasks**: One-to-Many relationship
  - A user can have many tasks
  - Tasks are deleted when user is deleted (cascade)

### Indexing Strategy

- Indexes on `username` and `email` for fast user lookups
- Index on `user_id` for efficient task queries
- Index on `completed` for filtering
- Index on `created_at` for sorting

## Authentication & Authorization

### Authentication Flow

1. User registers with username, email, password
2. Password is hashed using Werkzeug's `generate_password_hash`
3. User logs in with username and password
4. Flask-Login creates a session
5. Session is maintained via secure cookies

### Authorization

- Task ownership is checked in service layer
- Users can only access/modify their own tasks
- Routes use `@login_required` decorator
- Service methods verify ownership before operations

## Request Flow

### Example: Creating a Task

1. **Route** (`app/routes/tasks.py`):
   - Receives POST request to `/tasks/create`
   - Extracts form data (title, description)
   - Validates required fields
   - Calls `create_task()` service method

2. **Service** (`app/services/task_service.py`):
   - Validates business rules
   - Creates Task model instance
   - Saves to database
   - Returns Task object

3. **Model** (`app/models/task.py`):
   - SQLAlchemy handles database insertion
   - Sets timestamps automatically

4. **Route** (continued):
   - Receives Task object from service
   - Sets flash message
   - Redirects to task list

## Error Handling

### Exception Hierarchy

- **`ValidationError`**: Input validation failures
- **`TaskNotFoundError`**: Task doesn't exist
- **`TaskAccessDeniedError`**: User doesn't own task
- **`UserNotFoundError`**: User doesn't exist
- **`AuthenticationError`**: Authentication failures

### Error Handling Strategy

1. **Service Layer**: Raises custom exceptions
2. **Route Layer**: Catches exceptions and converts to user-friendly messages
3. **Error Pages**: Custom templates for 404 and 500 errors
4. **Logging**: All errors are logged for debugging

## Testing Strategy

### Test Organization

- **Unit Tests** (`tests/unit/`): Test individual components
  - Models: Test model methods and relationships
  - Services: Test business logic in isolation

- **Integration Tests** (`tests/integration/`): Test route handlers
  - Test HTTP requests/responses
  - Test database interactions
  - Test authentication flows

- **E2E Tests** (`tests/e2e/`): Test complete user flows
  - Registration → Login → Task Management
  - Full workflows from user perspective

### Test Fixtures

- **`app`**: Flask application instance with test database
- **`client`**: Test client for making requests
- **`user`**: Test user fixture
- **`authenticated_client`**: Authenticated test client
- **`task`**: Test task fixture
- **`another_user`**: Second user for access control tests

## Configuration Management

### Environment-Based Configuration

- **Development**: Debug mode enabled, SQLite database
- **Testing**: Test database, CSRF disabled
- **Production**: Debug disabled, production database

### Configuration Sources

1. Environment variables (`.env` file)
2. Flask config dictionary
3. Default values for development

## Security Considerations

### Password Security

- Passwords are never stored in plain text
- Uses Werkzeug's secure password hashing (PBKDF2)
- Password verification uses constant-time comparison

### Session Security

- Flask-Login manages secure sessions
- Session cookies are HTTP-only
- Secret key is required and should be strong

### SQL Injection Prevention

- SQLAlchemy ORM prevents SQL injection
- All queries use parameterized statements
- User input is validated before database operations

### Access Control

- Task ownership is verified at service layer
- Routes check authentication before processing
- Users cannot access other users' tasks

## Performance Optimizations

### Database

- Indexes on frequently queried fields
- Efficient queries using SQLAlchemy
- Pagination to limit result sets

### Caching Opportunities

- User sessions (handled by Flask-Login)
- Task lists could be cached (not implemented)

### Query Optimization

- Uses SQLAlchemy's `filter_by()` for indexed queries
- Lazy loading for relationships (can be optimized if needed)

## Scalability Considerations

### Current Limitations

- SQLite database (single-file, not suitable for high concurrency)
- No caching layer
- No background job processing
- Synchronous request handling

### Production Improvements

1. **Database**: Migrate to PostgreSQL or MySQL
2. **Caching**: Add Redis for session storage and caching
3. **Background Jobs**: Use Celery for async tasks
4. **Load Balancing**: Use Gunicorn/uWSGI with multiple workers
5. **CDN**: Serve static assets via CDN
6. **Monitoring**: Add application performance monitoring

## Code Organization Principles

### Separation of Concerns

- Routes handle HTTP concerns
- Services handle business logic
- Models handle data concerns
- Utils handle shared functionality

### DRY (Don't Repeat Yourself)

- Common functionality in services
- Reusable decorators
- Shared fixtures in tests

### Single Responsibility

- Each module has a clear, single purpose
- Functions are focused and small
- Classes represent single concepts

## Future Enhancements

### Potential Features

1. **Task Categories/Tags**: Organize tasks by category
2. **Due Dates**: Add due dates and reminders
3. **Task Sharing**: Share tasks between users
4. **File Attachments**: Attach files to tasks
5. **REST API**: Add JSON API endpoints
6. **Real-time Updates**: WebSocket support for live updates

### Technical Improvements

1. **API Versioning**: Add API versioning for future changes
2. **Rate Limiting**: Prevent abuse with rate limiting
3. **Audit Logging**: Log all operations for security
4. **Background Jobs**: Async task processing
5. **Full-text Search**: Advanced search capabilities

## Conclusion

This architecture provides a solid foundation for a Flask application with clear separation of concerns, comprehensive testing, and production-ready features. The layered approach makes the codebase maintainable and testable while following Flask best practices.

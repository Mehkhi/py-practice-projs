# Flask CRUD To-Do Application

A production-ready Flask web application for managing to-do tasks with user authentication, full CRUD operations, filtering, sorting, and pagination.

## Features

### Core Features

- **User Authentication**: Secure registration, login, and logout with password hashing
- **Task Management**: Full CRUD operations (Create, Read, Update, Delete) for tasks
- **Task Ownership**: Users can only access and modify their own tasks
- **Filtering**: Filter tasks by completion status (all, completed, incomplete)
- **Search**: Search tasks by title or description
- **Sorting**: Sort tasks by date, title, or completion status (ascending/descending)
- **Pagination**: Navigate through tasks with pagination (10 items per page)
- **Flash Messages**: User-friendly feedback messages for all operations
- **Error Handling**: Custom error pages for 404 and 500 errors
- **Responsive Design**: Clean, modern UI that works on all devices

### Technical Features

- **SQLAlchemy ORM**: Database abstraction layer with relationships
- **Alembic Migrations**: Database schema versioning and migrations
- **Flask-Login**: Session management and authentication
- **Type Hints**: Full type annotations throughout the codebase
- **Comprehensive Testing**: 25+ unit, integration, and E2E tests with >70% coverage
- **Structured Logging**: Detailed logging for debugging and monitoring
- **Code Quality**: Formatted with black, linted with ruff, type-checked with mypy

### Advanced Workflow Features

- **Kanban board** with drag-and-drop across Backlog/In Progress/Blocked/Review/Done plus critical-path highlighting
- **Smart scheduling** and **AI triage** suggest due dates, priorities, and seed acceptance criteria automatically
- **Recurring tasks & templates** so you can stamp repeating checklists with approvals and SLAs
- **Dependency graph + critical path** metrics to surface blockers and longest chains
- **Integrated time tracking** with per-task timers, burndown trend, and leaderboard of focus areas
- **Knowledge hub** with notes, acceptance criteria, retro entries, and link attachments per task
- **Collaboration trail** via audit logs and optional approval gates before Done

## Architecture Overview

The application follows a clean architecture pattern with separation of concerns:

- **Models**: Database models (`app/models/`)
- **Services**: Business logic layer (`app/services/`)
- **Routes**: HTTP request handlers (`app/routes/`)
- **Templates**: Jinja2 HTML templates (`app/templates/`)
- **Utils**: Utility functions and exceptions (`app/utils/`)

See [ARCHITECTURE.md](docs/ARCHITECTURE.md) for detailed architecture documentation.

## Installation and Setup

### Prerequisites

- Python 3.8 or higher
- pip package manager
- Virtual environment (recommended)

### Setup Instructions

1. **Clone or navigate to the project directory**:
   ```bash
   cd 01-flask-crud-to-do
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv

   # On macOS/Linux:
   source venv/bin/activate

   # On Windows:
   venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   Create a `.env` file in the project root (or copy from `.env.example`):
   ```bash
   SECRET_KEY=your-secret-key-change-in-production
   FLASK_ENV=development
   FLASK_DEBUG=1
   DATABASE_URL=sqlite:///todo_app.db
   SQLALCHEMY_TRACK_MODIFICATIONS=False
   ```

5. **Initialize the database**:
   ```bash
   flask db init
   flask db migrate -m "Initial migration"
   flask db upgrade
   ```

6. **Run the application**:
   ```bash
   python run.py
   ```

   Or using Flask CLI:
   ```bash
   export FLASK_APP=app
   flask run
   ```

7. **Access the application**:
   Open your web browser and navigate to `http://localhost:5000`

## Usage

### Basic Usage

1. **Register an account**:
   - Click "Register" on the navigation bar
   - Fill in username, email, and password (minimum 6 characters)
   - Click "Register" to create your account

2. **Login**:
   - Click "Login" on the navigation bar
   - Enter your username and password
   - Optionally check "Remember me" to stay logged in
   - Click "Login" to access your account

3. **Create a task**:
   - After logging in, click "Create New Task"
   - Enter a title (required) and optional description
   - Click "Create Task"

4. **View tasks**:
   - All your tasks are displayed on the "My Tasks" page
   - Use filters to show all, completed, or incomplete tasks
   - Use the search box to find tasks by title or description
   - Sort tasks by date, title, or status
   - Navigate through pages if you have more than 10 tasks

5. **Edit a task**:
   - Click "Edit" next to any task
   - Modify the title or description
   - Click "Update Task"

6. **Mark task as complete/incomplete**:
   - Click "Mark Complete" or "Mark Incomplete" button
   - The task status will toggle

7. **Delete a task**:
   - Click "Delete" next to any task
   - Confirm the deletion
   - The task will be permanently removed

### API Documentation

#### Authentication Routes

- `GET /auth/register` - Registration form
- `POST /auth/register` - Register new user
- `GET /auth/login` - Login form
- `POST /auth/login` - Authenticate user
- `GET /auth/logout` - Logout user

#### Task Routes

- `GET /tasks/` - List all tasks (with filtering, sorting, pagination)
  - Query parameters:
    - `completed`: Filter by status (`true`, `false`, or omitted for all)
    - `search`: Search term for title/description
    - `sort_by`: Sort field (`created_at`, `title`, `completed`)
    - `order`: Sort order (`asc`, `desc`)
    - `page`: Page number (default: 1)

- `GET /tasks/new` - Show create task form
- `POST /tasks/create` - Create new task
- `GET /tasks/<id>/edit` - Show edit task form
- `POST /tasks/<id>/update` - Update task
- `POST /tasks/<id>/delete` - Delete task
- `POST /tasks/<id>/toggle` - Toggle task completion

## Configuration Options

### Environment Variables

- `SECRET_KEY`: Flask secret key for session management (required)
- `FLASK_ENV`: Environment mode (`development`, `production`, `testing`)
- `FLASK_DEBUG`: Enable debug mode (`1` or `0`)
- `DATABASE_URL`: Database connection string (default: `sqlite:///todo_app.db`)
- `SQLALCHEMY_TRACK_MODIFICATIONS`: Track modifications flag (default: `False`)

### Database Configuration

The application uses SQLite by default for development. For production, you can use PostgreSQL or MySQL by changing the `DATABASE_URL`:

```bash
# PostgreSQL
DATABASE_URL=postgresql://user:password@localhost/todo_app

# MySQL
DATABASE_URL=mysql://user:password@localhost/todo_app
```

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/unit/test_models.py

# Run with verbose output
pytest -v
```

### Code Quality

```bash
# Format code with black
black app tests

# Lint with ruff
ruff check app tests

# Type check with mypy
mypy app
```

### Database Migrations

```bash
# Create a new migration
flask db migrate -m "Description of changes"

# Apply migrations
flask db upgrade

# Rollback last migration
flask db downgrade
```

## Testing

The project includes comprehensive test coverage:

- **Unit Tests**: Test individual components (models, services)
- **Integration Tests**: Test route handlers and database interactions
- **E2E Tests**: Test complete user flows

Test coverage is maintained above 70% as required.

### Running Tests

```bash
# All tests
pytest

# With coverage
pytest --cov=app --cov-report=term-missing

# Specific test categories
pytest tests/unit/
pytest tests/integration/
pytest tests/e2e/
```

## Troubleshooting

### Common Issues

1. **Database errors**:
   - Ensure the database file has write permissions
   - Run migrations: `flask db upgrade`
   - Check `DATABASE_URL` environment variable

2. **Import errors**:
   - Ensure virtual environment is activated
   - Install dependencies: `pip install -r requirements.txt`
   - Check Python version (3.8+)

3. **Login not working**:
   - Check that `SECRET_KEY` is set
   - Verify Flask-Login is properly configured
   - Check browser cookies are enabled

4. **Tests failing**:
   - Ensure test database is properly configured
   - Check that all dependencies are installed
   - Verify test fixtures are working

### Debug Mode

Enable debug mode for detailed error messages:

```bash
export FLASK_DEBUG=1
python run.py
```

**Warning**: Never enable debug mode in production!

## Performance Considerations

- **Database Indexing**: User and Task models have indexes on frequently queried fields
- **Pagination**: Large task lists are paginated to improve performance
- **Query Optimization**: Uses SQLAlchemy's efficient query methods
- **Session Management**: Flask-Login handles efficient session storage

For production deployments:
- Use a production-grade database (PostgreSQL recommended)
- Enable database connection pooling
- Use a production WSGI server (Gunicorn, uWSGI)
- Set up proper logging and monitoring
- Use environment variables for sensitive configuration

## Security Considerations

- **Password Hashing**: Uses Werkzeug's secure password hashing
- **Session Security**: Flask-Login manages secure sessions
- **SQL Injection Protection**: SQLAlchemy ORM prevents SQL injection
- **CSRF Protection**: Can be enabled with Flask-WTF (disabled in tests)
- **Input Validation**: All user inputs are validated

## Project Structure

```
01-flask-crud-to-do/
├── app/
│   ├── __init__.py              # Flask app factory
│   ├── models/                  # Database models
│   │   ├── user.py
│   │   └── task.py
│   ├── routes/                  # Route handlers
│   │   ├── auth.py
│   │   ├── tasks.py
│   │   └── main.py
│   ├── services/                # Business logic
│   │   ├── auth_service.py
│   │   └── task_service.py
│   ├── utils/                   # Utilities
│   │   ├── decorators.py
│   │   └── exceptions.py
│   └── templates/               # Jinja2 templates
│       ├── base.html
│       ├── auth/
│       ├── tasks/
│       └── errors/
├── tests/                       # Test suite
│   ├── conftest.py
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── migrations/                  # Alembic migrations
├── docs/                        # Documentation
│   └── ARCHITECTURE.md
├── requirements.txt             # Dependencies
├── pyproject.toml               # Project configuration
├── run.py                       # Application entry point
└── README.md                    # This file
```

## License

This project is part of a learning exercise and is provided as-is for educational purposes.

## Contributing

This is a learning project. Feel free to fork and experiment!

## Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [SQLAlchemy Documentation](https://www.sqlalchemy.org/)
- [Flask-Login Documentation](https://flask-login.readthedocs.io/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)

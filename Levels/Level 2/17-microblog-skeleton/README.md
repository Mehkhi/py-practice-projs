# Microblog

A simple Flask-based microblogging application that allows users to register, login, create posts, and view content from other users.

## Features

### Core Features
- **User Authentication**: Registration and login system with secure password hashing
- **Post Management**: Create, view, and manage blog posts
- **User Profiles**: View user profiles and their posts
- **Session Management**: Secure session handling with Flask-Login
- **Responsive Design**: Clean, mobile-friendly interface
- **Pagination**: Navigate through posts efficiently

### Technical Features
- **SQLite Database**: Lightweight database for data persistence
- **Flask Framework**: Modern web framework for Python
- **WTForms**: Secure form handling and validation
- **Jinja2 Templates**: Dynamic template rendering
- **Comprehensive Testing**: Full test suite with pytest
- **Error Handling**: Graceful error handling and logging
- **Type Hints**: Full type annotation support

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Setup Instructions

1. **Clone or download the project**:
   ```bash
   cd 17-microblog-skeleton
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

4. **Run the application**:
   ```bash
   python -m microblog
   ```

5. **Access the application**:
   Open your web browser and navigate to `http://localhost:5000`

## Usage

### Basic Usage

1. **Register an account**:
   - Click "Register" on the navigation bar
   - Fill in username, email, password, and optional bio
   - Click "Register" to create your account

2. **Login**:
   - Click "Login" on the navigation bar
   - Enter your username and password
   - Click "Sign In" to access your account

3. **Create a post**:
   - After logging in, click "Create Post"
   - Enter a title and content for your post
   - Click "Post" to publish

4. **View posts**:
   - The home page shows all posts in reverse chronological order
   - Click on any post title to view the full content
   - Click on author names to view their profiles

5. **View profiles**:
   - Click on any username to view their profile
   - See all posts by that user with pagination

### Configuration Options

The application can be configured using environment variables:

- `SECRET_KEY`: Flask secret key (defaults to development key)
- `DATABASE_URL`: Database connection URL (defaults to `sqlite:///microblog.db`)

Example:
```bash
export SECRET_KEY="your-secret-key-here"
export DATABASE_URL="sqlite:///custom.db"
python -m microblog
```

## Development

### Running Tests

Run the test suite to verify functionality:

```bash
# Run all tests
pytest tests/

# Run with verbose output
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=microblog
```

### Code Quality

The project includes tools for maintaining code quality:

```bash
# Format code with black
black microblog/ tests/

# Lint code with ruff
ruff check microblog/ tests/

# Type checking with mypy (optional)
mypy microblog/
```

### Project Structure

```
17-microblog-skeleton/
├── microblog/                    # Main application package
│   ├── __init__.py              # Application factory
│   ├── __main__.py              # Entry point
│   ├── models.py                # Database models
│   ├── forms.py                 # WTForms definitions
│   ├── routes.py                # Route definitions
│   ├── templates/               # Jinja2 templates
│   │   ├── base.html           # Base template
│   │   ├── index.html          # Home page
│   │   ├── login.html          # Login page
│   │   ├── register.html       # Registration page
│   │   ├── create_post.html    # Post creation
│   │   ├── view_post.html      # Single post view
│   │   └── profile.html        # User profile
│   └── static/                  # Static files (CSS, JS, images)
├── tests/                       # Test suite
│   ├── __init__.py
│   └── test_microblog.py       # Main test file
├── requirements.txt             # Python dependencies
├── README.md                   # This file
├── CHECKLIST.md                # Feature checklist
└── SPEC.md                     # Project specification
```

## API Endpoints

### Public Routes
- `GET /` - Home page (all posts)
- `GET /post/<id>` - View single post
- `GET /profile/<username>` - View user profile

### Authentication Routes
- `GET /auth/login` - Login page
- `POST /auth/login` - Process login
- `GET /auth/register` - Registration page
- `POST /auth/register` - Process registration
- `GET /auth/logout` - Logout (requires login)

### Protected Routes
- `GET /create` - Create post form (requires login)
- `POST /create` - Process post creation (requires login)

## Database Schema

### Users Table
- `id` (Integer, Primary Key)
- `username` (String, Unique, Not Null)
- `email` (String, Unique, Not Null)
- `password_hash` (String, Not Null)
- `bio` (Text, Optional)
- `created_at` (DateTime)

### Posts Table
- `id` (Integer, Primary Key)
- `title` (String, Not Null)
- `content` (Text, Not Null)
- `created_at` (DateTime)
- `updated_at` (DateTime)
- `user_id` (Integer, Foreign Key to users.id)

## Security Features

- **Password Hashing**: Uses Werkzeug's secure password hashing
- **Session Security**: Flask-Login manages secure sessions
- **CSRF Protection**: Flask-WTF provides CSRF protection for forms
- **Input Validation**: WTForms validates all user inputs
- **SQL Injection Prevention**: SQLAlchemy ORM prevents SQL injection

## Logging

The application includes comprehensive logging:
- INFO level for normal operations (user actions, page views)
- ERROR level for exceptions and errors
- WARNING level for failed login attempts

Logs are written to console in development mode.

## Known Limitations

1. **No Email Verification**: Users can register without email verification
2. **No Password Reset**: Forgot password functionality not implemented
3. **No Post Editing**: Posts cannot be edited after creation
4. **No Post Deletion**: Posts cannot be deleted
5. **No User Following**: No follow/unfollow functionality
6. **No Search**: No search functionality for posts or users
7. **Single Database**: Uses SQLite, not suitable for high-traffic production
8. **No File Uploads**: No support for image or file uploads

## Future Enhancements

Potential improvements for future versions:
- Email verification and password reset
- Post editing and deletion
- User following system
- Search functionality
- Comment system
- Like/upvote system
- File upload support
- Production database support (PostgreSQL, MySQL)
- API endpoints for mobile apps
- Admin panel
- Email notifications

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## License

This project is for educational purposes as part of a Python learning curriculum.

## Support

For issues or questions:
1. Check the test suite for expected behavior
2. Review the code comments and documentation
3. Check the logs for error messages
4. Ensure all dependencies are properly installed

## Performance Considerations

- Pagination limits database queries to 10 posts per page
- Database indexes on frequently queried fields (username, email, created_at)
- Efficient query patterns using SQLAlchemy ORM
- Minimal static assets for fast loading

## Testing Strategy

The test suite covers:
- Model functionality and relationships
- Route behavior and responses
- Form validation and processing
- Authentication and authorization
- Edge cases and error conditions
- Database constraints and operations

Tests use an in-memory SQLite database for isolation and speed.

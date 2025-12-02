# To-Do List GUI Application

A comprehensive to-do list management application with a graphical user interface built using Python and Tkinter. This application provides an intuitive way to manage tasks with features like priority management, due dates, search functionality, and persistent storage.

## Features

### Core Features
- ✅ **Task Management**: Create, edit, delete, and mark tasks as complete
- ✅ **Priority System**: Set task priorities (low, medium, high) with color coding
- ✅ **Due Dates**: Add due dates to tasks with date picker
- ✅ **Search & Filter**: Search tasks by title/description and filter by status
- ✅ **Persistent Storage**: All tasks are saved to JSON file automatically
- ✅ **Statistics**: View task statistics and completion rates
- ✅ **Input Validation**: Comprehensive validation for all user inputs

### User Interface
- Clean, modern Tkinter-based GUI
- Intuitive task list with checkboxes
- Priority color coding (red=high, orange=medium, green=low)
- Search and filter controls
- Edit dialog for detailed task modification
- Status bar with real-time feedback

## Installation

### Prerequisites
- Python 3.8 or higher
- Tkinter (included with Python standard library)

### Setup Instructions

1. **Clone or download the project**
   ```bash
   git clone <repository-url>
   cd 11-to-do-gui
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv venv

   # On Windows
   venv\Scripts\activate

   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python -m to_do_gui
   ```

## Usage

### Starting the Application

```bash
# Run from the project directory
python -m to_do_gui

# Or run the main module directly
python to_do_gui/main.py
```

### Basic Operations

#### Adding a Task
1. Enter task title in the "Title" field
2. Select priority from the dropdown (low, medium, high)
3. Optionally enter due date in YYYY-MM-DD format
4. Click "Add Task" or press Enter

#### Managing Tasks
- **Edit**: Double-click a task or select and click "Edit Task"
- **Delete**: Select a task and click "Delete Task"
- **Toggle Complete**: Select a task and click "Toggle Complete"
- **Clear Completed**: Remove all completed tasks at once

#### Search and Filter
- **Search**: Type in the search box to find tasks by title or description
- **Filter**: Use radio buttons to show All, Active, or Completed tasks
- **Priority Colors**: Tasks are color-coded by priority in the list

### Advanced Features

#### Task Priorities
- **High Priority**: Red color coding
- **Medium Priority**: Orange color coding
- **Low Priority**: Green color coding

#### Due Dates
- Enter dates in YYYY-MM-DD format
- Due dates are displayed in the task list
- Empty due date field shows placeholder text

#### Statistics
- Click "Statistics" to view:
  - Total number of tasks
  - Completed vs incomplete tasks
  - Task distribution by priority

## Configuration

### Data Storage
- Tasks are automatically saved to `tasks.json` in the application directory
- The file is created automatically on first run
- Data persists between application sessions

### Logging
- Application logs are written to `todo_app.log`
- Log level can be modified in `main.py`
- Logs include task operations and error messages

## Project Structure

```
11-to-do-gui/
├── to_do_gui/              # Main package
│   ├── __init__.py         # Package initialization
│   ├── main.py             # Application entry point
│   ├── core.py             # Task and TaskManager classes
│   └── gui.py              # Tkinter GUI implementation
├── tests/                  # Unit tests
│   ├── __init__.py
│   └── test_to_do_gui.py   # Comprehensive test suite
├── requirements.txt        # Dependencies
├── README.md              # This file
├── CHECKLIST.md           # Feature checklist
└── SPEC.md                # Project specification
```

## Testing

The application includes a comprehensive test suite with 15+ unit tests covering:

- Task creation and manipulation
- TaskManager operations
- Data persistence
- Error handling
- Edge cases

### Running Tests

```bash
# Run all tests
pytest tests/

# Run with verbose output
pytest tests/ -v

# Run specific test file
pytest tests/test_to_do_gui.py

# Run with coverage
pytest tests/ --cov=to_do_gui
```

### Test Coverage
- Task class functionality
- TaskManager CRUD operations
- File persistence (save/load)
- Search and filtering
- Error handling and edge cases
- Data validation

## Development

### Code Quality
- Type hints on all public functions
- Comprehensive docstrings
- PEP 8 compliant code style
- Error handling with proper logging
- Modular architecture

### Adding Features
The codebase is designed for easy extension:

1. **New Task Properties**: Add fields to the `Task` class
2. **GUI Components**: Extend the `TodoGUI` class
3. **Data Operations**: Add methods to `TaskManager`
4. **Validation**: Update validation logic in GUI methods

### Dependencies
- **Tkinter**: GUI framework (Python standard library)
- **json**: Data serialization (Python standard library)
- **datetime**: Date/time handling (Python standard library)
- **pathlib**: File path operations (Python standard library)
- **logging**: Application logging (Python standard library)

## Known Limitations

1. **Single User**: No multi-user support
2. **Local Storage Only**: No cloud synchronization
3. **No Categories**: Tasks cannot be organized into categories
4. **No Recurring Tasks**: No support for repeating tasks
5. **No Attachments**: Cannot attach files to tasks
6. **No Notifications**: No reminder or notification system

## Troubleshooting

### Common Issues

**Application won't start**
- Ensure Python 3.8+ is installed
- Check that Tkinter is available: `python -c "import tkinter"`
- Verify all files are in the correct directory structure

**Tasks not saving**
- Check file permissions in the application directory
- Ensure `tasks.json` is not locked by another process
- Check application logs in `todo_app.log`

**GUI not displaying properly**
- Try different Tkinter themes
- Check display resolution and scaling settings
- Ensure sufficient screen space (minimum 600x400)

**Search not working**
- Search is case-sensitive
- Try different search terms
- Check if filters are applied

### Getting Help

1. Check the application logs in `todo_app.log`
2. Run tests to verify installation: `pytest tests/`
3. Review error messages in the GUI status bar
4. Ensure all dependencies are properly installed

## License

This project is part of a Python learning curriculum and is intended for educational purposes.

## Contributing

This is a learning project, but suggestions for improvements are welcome:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## Changelog

### Version 1.0.0
- Initial release
- Core task management functionality
- Tkinter GUI interface
- Priority system with color coding
- Due date support
- Search and filter capabilities
- JSON persistence
- Comprehensive test suite
- Complete documentation

# 20-task-scheduler

## Project: Task Scheduler

**Level**: 2 (Junior)
**Difficulty**: 2-3/5
**Time Estimate**: 1-3 days

## Overview

This is an intermediate Python project that teaches practical tool development. You'll work with external libraries, APIs, databases, or file formats while building a useful command-line utility that solves real-world problems.

## What You're Building

A professional CLI tool that demonstrates:
- Third-party library integration
- API consumption or file processing
- Data persistence (files or databases)
- Error handling and logging
- Well-structured code architecture
- User-friendly interface

## Learning Objectives

By completing this project, you will:
1. Integrate and use popular Python libraries
2. Work with external data sources (APIs, files, databases)
3. Implement proper error handling and validation
4. Structure code into modules and functions
5. Write comprehensive tests
6. Create user documentation
7. Handle edge cases and error conditions
8. Use logging for debugging and monitoring

## Core Concepts

This project focuses on:
- **Library Usage**: Working with established Python packages
- **Data Processing**: Parsing, transforming, and storing data
- **API Integration**: HTTP requests, JSON parsing, authentication
- **Persistence**: Files (JSON, CSV) or databases (SQLite)
- **Code Organization**: Modules, classes, and functions
- **Testing**: Unit tests with pytest
- **Documentation**: READMEs, docstrings, examples

## Technical Skills

You'll practice:
- Package management with pip and requirements.txt
- Working with common libraries (requests, pandas, BeautifulSoup, etc.)
- Command-line argument parsing with argparse
- Database operations (SQL queries, ORMs)
- File format handling (CSV, JSON, PDF, images)
- Error handling patterns
- Logging with the logging module
- Type hints for better code clarity
- Testing with pytest

## Requirements

### Functional Requirements

See CHECKLIST.md for detailed feature requirements.

### Non-Functional Requirements

- **Code Quality**: Well-organized, modular code with clear naming
- **Testing**: 8-12 unit tests covering core functionality
- **Documentation**: README with installation and usage examples
- **Error Handling**: Graceful handling of all error conditions
- **Logging**: Appropriate INFO and ERROR logging
- **Performance**: Reasonable speed for typical use cases

## Architecture

### Recommended Structure

```
20-task-scheduler/
├── task_scheduler/      # Package directory
│   ├── __init__.py
│   ├── main.py                     # Entry point
│   ├── core.py                     # Core logic
│   └── utils.py                    # Helper functions
├── tests/
│   ├── __init__.py
│   └── test_task_scheduler.py
├── requirements.txt                # Dependencies
├── README.md                       # Documentation
├── CHECKLIST.md                    # Feature checklist
└── SPEC.md                         # This file
```

## Getting Started

### Prerequisites

- Python 3.8 or higher
- pip for package management
- Virtual environment (recommended)

### Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the program
python -m task_scheduler [arguments]
```

### Development Workflow

1. **Plan**: Review CHECKLIST.md and understand requirements
2. **Setup**: Create project structure and install dependencies
3. **Implement**: Build features incrementally
4. **Test**: Write tests as you go
5. **Document**: Update README with usage examples
6. **Refine**: Improve error handling and edge cases

## Testing

This level requires comprehensive testing:

```python
# Example test structure
def test_core_functionality():
    # Test happy path
    pass

def test_edge_cases():
    # Test boundaries and unusual inputs
    pass

def test_error_handling():
    # Test error conditions
    pass
```

Run tests with: `pytest tests/`

## Success Criteria

Your project is complete when:
- ✅ All required features work correctly
- ✅ 8-12 tests pass with good coverage
- ✅ Code is well-organized into modules
- ✅ Error handling is comprehensive
- ✅ Logging provides useful information
- ✅ README documents installation and usage
- ✅ Type hints on public functions
- ✅ Code passes linting (ruff/flake8)

## Common Pitfalls

- **Poor error handling**: Always validate external data
- **No logging**: Add logging for debugging production issues
- **Monolithic code**: Break code into small, testable functions
- **Missing tests**: Write tests for both success and failure cases
- **Hardcoded values**: Use configuration files or environment variables
- **No input validation**: Never trust user input or external data

## Extension Ideas

After completing the basic requirements:
- Add bonus features from CHECKLIST.md
- Improve performance with caching or async operations
- Add a simple web interface with Flask
- Create a package and publish to TestPyPI
- Add CI/CD with GitHub Actions
- Implement additional output formats
- Add progress bars for long operations

## Resources

### Python Libraries
- Official Package Index: https://pypi.org/
- Library Documentation: Check each library's docs

### Development Tools
- pytest: https://docs.pytest.org/
- argparse: https://docs.python.org/3/library/argparse.html
- logging: https://docs.python.org/3/howto/logging.html

### Best Practices
- PEP 8 Style Guide: https://pep8.org/
- Type Hints: https://docs.python.org/3/library/typing.html

## Notes

- Use virtual environments to manage dependencies
- Write docstrings for all public functions
- Test with different inputs and edge cases
- Keep functions small and focused
- Use meaningful variable and function names
- Don't reinvent the wheel - use established libraries

---

**Remember**: Focus on building practical, maintainable tools. This is about applying Python to solve real problems with professional code quality.

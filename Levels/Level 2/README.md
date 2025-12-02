# Task Scheduler

A command-line task scheduler that allows you to schedule tasks with cron-like syntax. Supports executing shell commands or Python functions with persistent storage and error handling.

## Features

- Schedule tasks using cron expressions
- Execute shell commands or Python functions
- Persistent storage of scheduled tasks (JSON)
- Logging of task executions
- Error handling with retry logic
- Command-line interface for managing tasks

## Installation

1. Clone or download the project
2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Adding a Task

#### Shell Command
```bash
python -m task_scheduler add --id backup --cron "0 2 * * *" --type shell --command "tar -czf backup.tar.gz /home/user/data"
```

#### Python Function
```bash
python -m task_scheduler add --id cleanup --cron "0 3 * * *" --type python --module mymodule --function cleanup_function
```

### Listing Tasks
```bash
python -m task_scheduler list
```

### Removing a Task
```bash
python -m task_scheduler remove --id backup
```

### Running the Scheduler
```bash
python -m task_scheduler run
```

Use Ctrl+C to stop the scheduler.

## Cron Expressions

Cron expressions consist of 5 fields: minute, hour, day of month, month, day of week.

Examples:
- `* * * * *` - Every minute
- `0 * * * *` - Every hour at minute 0
- `0 2 * * *` - Daily at 2:00 AM
- `0 0 * * 1` - Every Monday at midnight
- `*/15 * * * *` - Every 15 minutes

## Configuration

Tasks are stored in `tasks.json` in the current directory. You can specify a different file by modifying the `Scheduler` class.

## Known Limitations

- Scheduler must be running for tasks to execute
- No web interface (bonus feature not implemented)
- No email notifications on failure
- No concurrent execution of tasks
- Python functions must be importable from the current environment

## Examples

### Backup Script
```bash
python -m task_scheduler add --id daily_backup --cron "0 2 * * *" --type shell --command "rsync -av /source /backup"
python -m task_scheduler run
```

### Python Cleanup Function
Create a file `cleanup.py`:
```python
def cleanup_temp():
    import os
    import shutil
    # Your cleanup code here
    pass
```

Then add the task:
```bash
python -m task_scheduler add --id temp_cleanup --cron "0 */6 * * *" --type python --module cleanup --function cleanup_temp
```

## Development

Run tests:
```bash
pytest tests/
```

## License

This project is open source.

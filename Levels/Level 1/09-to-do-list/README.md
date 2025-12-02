# To-Do List Manager

A command-line to-do list application with task management, priority levels, and JSON persistence.

## What It Does

This program provides a complete task management system that:
- Add new tasks with priority levels (high, medium, low)
- Mark tasks as complete or incomplete
- List all tasks with status indicators
- Search and filter tasks
- Delete tasks
- Save and load tasks from JSON file
- Display task statistics

## How to Run

1. Make sure you have Python 3.7 or higher installed
2. Run the program:
   ```bash
   python to_do_list.py
   ```
3. Follow the menu prompts to manage your tasks

## Example Usage

### Adding a Task
```
[MEMO] TO-DO LIST MANAGER
========================================
1. Add new task
2. List tasks
3. Complete task
4. Manage task
5. Show statistics
6. Exit
========================================
Enter your choice (1-6): 1

=== Add New Task ===
Enter task description: Buy groceries

Priority levels:
1. High
2. Medium
3. Low
Select priority (1-3, default=2): 1
[OK] Task added: Buy groceries
```

### Listing Tasks
```
=== List Tasks ===
1. All tasks
2. Pending tasks only
3. Completed tasks only
4. Search tasks
Select option (1-4): 1

============================================================
[CLIPBOARD] TO-DO LIST
============================================================
 1. [O] [RED CIRCLE] Buy groceries
 2. [OK] [YELLOW CIRCLE] Walk the dog
       Completed: 2024-01-15
 3. [O] [GREEN CIRCLE] Read a book
============================================================
```

### Task Statistics
```
[BAR CHART] TASK STATISTICS
========================================
Total tasks:     3
Completed:       1
Pending:         2
Completion rate: 33.3%
========================================
```

## Features

### Core Features
- **Task Management**: Add, complete, delete tasks
- **Priority Levels**: High ([RED CIRCLE]), Medium ([YELLOW CIRCLE]), Low ([GREEN CIRCLE])
- **Status Tracking**: Visual indicators for completed ([OK]) and pending ([O]) tasks
- **JSON Persistence**: Automatic saving and loading of tasks
- **Search**: Find tasks by description
- **Filtering**: View all, pending, or completed tasks
- **Statistics**: Track completion rates and task counts

### User Interface
- **Interactive Menu**: Easy-to-navigate command-line interface
- **Visual Indicators**: Emojis for priority and status
- **Formatted Display**: Clean, readable task listings
- **Error Handling**: Graceful handling of invalid input

## Data Storage

Tasks are automatically saved to `todos.json` in the same directory as the script. Each task contains:

```json
{
  "id": 1,
  "description": "Buy groceries",
  "completed": false,
  "priority": "high",
  "created_at": "2024-01-15T10:30:00.000000",
  "completed_at": null
}
```

## Priority Levels

- **High** ([RED CIRCLE]): Urgent and important tasks
- **Medium** ([YELLOW CIRCLE]): Important but not urgent tasks
- **Low** ([GREEN CIRCLE]): Nice-to-have tasks

## Menu Options

1. **Add new task**: Create a new task with description and priority
2. **List tasks**: View tasks (all, pending, completed, or search)
3. **Complete task**: Mark pending tasks as completed
4. **Manage task**: Mark tasks as incomplete or delete them
5. **Show statistics**: View task completion statistics
6. **Exit**: Save and quit the application

## Testing

Run the unit tests:
```bash
python -m pytest test_to_do_list.py -v
```

Or run with unittest:
```bash
python test_to_do_list.py
```

## Keyboard Controls

- **Ctrl+C**: Exit the application at any time
- **Ctrl+D**: Exit the application at any time

## Examples

### Task Management Workflow
```bash
# Add tasks
1. Add new task -> "Finish project" -> High priority
1. Add new task -> "Buy milk" -> Medium priority
1. Add new task -> "Call mom" -> Low priority

# Complete tasks
3. Complete task -> Select "Finish project"

# View progress
2. List tasks -> 1. All tasks
5. Show statistics

# Clean up
4. Manage task -> Select "Buy milk" -> Delete
```

### Search Example
```bash
2. List tasks -> 4. Search tasks
Enter search term: buy
# Shows: "Buy milk"
```

## File Operations

- **Auto-save**: Tasks are saved automatically after any change
- **Auto-load**: Tasks are loaded when the application starts
- **Backup**: You can manually backup `todos.json` file
- **Reset**: Delete `todos.json` to start with a clean slate

## Error Handling

The application handles various error conditions:
- Invalid menu choices
- Empty task descriptions
- Invalid task numbers
- File I/O errors (with fallback to empty list)
- Keyboard interrupts (graceful exit)

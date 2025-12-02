import importlib
import json
import logging
import subprocess
import time
from datetime import datetime

from .utils import CronSchedule


class Task:
    """Represents a scheduled task with cron expression and execution details."""

    def __init__(self, id: str, cron_expr: str, task_type: str, command: str,
                 module: str = None, function: str = None, retries: int = 3):
        self.id = id
        self.cron_expr = cron_expr
        self.task_type = task_type  # 'shell' or 'python'
        self.command = command
        self.module = module
        self.function = function
        self.retries = retries
        self._cron_schedule = CronSchedule(cron_expr, base_time=datetime.now())

    def get_next_run(self) -> datetime:
        """Get the next scheduled run time."""
        return self._cron_schedule.get_next()

    def execute(self) -> None:
        """Execute the task with retry logic."""
        logging.info(f"Executing task {self.id}")
        try:
            if self.task_type == 'shell':
                result = subprocess.run(self.command, shell=True, capture_output=True, text=True, timeout=300)
                if result.returncode != 0:
                    raise Exception(f"Shell command failed: {result.stderr}")
            elif self.task_type == 'python':
                mod = importlib.import_module(self.module)
                func = getattr(mod, self.function)
                func()
            logging.info(f"Task {self.id} completed successfully")
        except Exception as e:
            logging.error(f"Task {self.id} failed: {e}")
            # Retry logic with exponential backoff
            for attempt in range(1, self.retries + 1):
                try:
                    time.sleep(2 ** attempt)  # Exponential backoff
                    if self.task_type == 'shell':
                        result = subprocess.run(self.command, shell=True, capture_output=True, text=True, timeout=300)
                        if result.returncode == 0:
                            logging.info(f"Task {self.id} succeeded on retry {attempt}")
                            return
                    elif self.task_type == 'python':
                        mod = importlib.import_module(self.module)
                        func = getattr(mod, self.function)
                        func()
                        logging.info(f"Task {self.id} succeeded on retry {attempt}")
                        return
                except Exception as e2:
                    logging.error(f"Task {self.id} retry {attempt} failed: {e2}")
            logging.error(f"Task {self.id} failed after {self.retries} retries")


class Scheduler:
    """Manages a collection of scheduled tasks."""

    def __init__(self, storage_file: str = 'tasks.json'):
        self.storage_file = storage_file
        self.tasks = []
        self._next_runs = {}
        self.load_tasks()
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    def load_tasks(self) -> None:
        """Load tasks from persistent storage."""
        try:
            with open(self.storage_file, 'r') as f:
                data = json.load(f)
                for item in data:
                    task = Task(**item)
                    self._register_task(task)
        except FileNotFoundError:
            logging.info("No existing tasks file found, starting fresh")
        except json.JSONDecodeError as e:
            logging.error(f"Error loading tasks: {e}")

    def save_tasks(self) -> None:
        """Save tasks to persistent storage."""
        data = [{
            'id': t.id,
            'cron_expr': t.cron_expr,
            'task_type': t.task_type,
            'command': t.command,
            'module': t.module,
            'function': t.function,
            'retries': t.retries
        } for t in self.tasks]
        with open(self.storage_file, 'w') as f:
            json.dump(data, f, indent=4)

    def add_task(self, task: Task) -> None:
        """Add a new task to the scheduler."""
        self._register_task(task)
        self.save_tasks()
        logging.info(f"Added task {task.id}")

    def remove_task(self, task_id: str) -> bool:
        """Remove a task by ID."""
        for i, task in enumerate(self.tasks):
            if task.id == task_id:
                del self.tasks[i]
                self._next_runs.pop(task, None)
                self.save_tasks()
                logging.info(f"Removed task {task_id}")
                return True
        logging.warning(f"Task {task_id} not found")
        return False

    def list_tasks(self) -> list:
        """List all tasks."""
        return self.tasks

    def run(self) -> None:
        """Run the scheduler loop."""
        logging.info("Scheduler started")
        try:
            while True:
                now = datetime.now()
                if not self._next_runs:
                    time.sleep(60)  # No tasks, sleep for 1 minute
                    continue

                due_tasks = [task for task, run_at in self._next_runs.items() if run_at <= now]

                if due_tasks:
                    for task in due_tasks:
                        task.execute()
                        self._next_runs[task] = task.get_next_run()
                    continue

                next_time = min(self._next_runs.values())
                sleep_time = max((next_time - now).total_seconds(), 0)
                time.sleep(min(sleep_time, 60))  # Max sleep 1 minute to allow for interruptions
        except KeyboardInterrupt:
            logging.info("Scheduler stopped by user")
        except Exception as e:
            logging.error(f"Scheduler error: {e}")

    def _register_task(self, task: Task) -> None:
        """Track a task's upcoming run without altering other schedules."""
        self.tasks.append(task)
        self._next_runs[task] = task.get_next_run()

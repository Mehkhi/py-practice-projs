#!/usr/bin/env python3
"""Command-line interface for the Task Scheduler."""

import argparse
import sys
from .core import Scheduler, Task


def main():
    parser = argparse.ArgumentParser(description="Task Scheduler CLI")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Add task
    add_parser = subparsers.add_parser('add', help='Add a new task')
    add_parser.add_argument('--id', required=True, help='Task ID')
    add_parser.add_argument('--cron', required=True, help='Cron expression')
    add_parser.add_argument('--type', required=True, choices=['shell', 'python'], help='Task type')
    add_parser.add_argument('--command', required=True, help='Command to execute')
    add_parser.add_argument('--module', help='Python module (for python type)')
    add_parser.add_argument('--function', help='Python function (for python type)')
    add_parser.add_argument('--retries', type=int, default=3, help='Number of retries')

    # Remove task
    remove_parser = subparsers.add_parser('remove', help='Remove a task')
    remove_parser.add_argument('--id', required=True, help='Task ID to remove')

    # List tasks
    list_parser = subparsers.add_parser('list', help='List all tasks')

    # Run scheduler
    run_parser = subparsers.add_parser('run', help='Run the scheduler')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    scheduler = Scheduler()

    if args.command == 'add':
        if args.type == 'python' and (not args.module or not args.function):
            print("Error: --module and --function required for python tasks")
            sys.exit(1)
        task = Task(
            id=args.id,
            cron_expr=args.cron,
            task_type=args.type,
            command=args.command,
            module=args.module,
            function=args.function,
            retries=args.retries
        )
        scheduler.add_task(task)
        print(f"Task {args.id} added successfully")

    elif args.command == 'remove':
        if scheduler.remove_task(args.id):
            print(f"Task {args.id} removed successfully")
        else:
            print(f"Task {args.id} not found")
            sys.exit(1)

    elif args.command == 'list':
        tasks = scheduler.list_tasks()
        if not tasks:
            print("No tasks scheduled")
        else:
            print("Scheduled tasks:")
            for task in tasks:
                print(f"- ID: {task.id}, Cron: {task.cron_expr}, Type: {task.task_type}, Command: {task.command}")

    elif args.command == 'run':
        try:
            scheduler.run()
        except KeyboardInterrupt:
            print("\nScheduler stopped")


if __name__ == '__main__':
    main()

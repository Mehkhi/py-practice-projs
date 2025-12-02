"""
Core business logic for the Flask Mini API.

This module contains the main data management classes and operations.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import sqlite3
import json
import os

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages SQLite database operations."""

    def __init__(self, db_path: str = "flask_mini_api.db"):
        """Initialize database manager."""
        self.db_path = db_path
        self.connection: Optional[sqlite3.Connection] = None

    def close_connection(self) -> None:
        """Close any existing database connection."""
        if self.connection is not None:
            try:
                self.connection.close()
            except sqlite3.Error as exc:
                logger.debug(f"Error closing database connection: {exc}")
            finally:
                self.connection = None

    def init_database(self, reset: bool = False):
        """Initialize database tables."""
        try:
            reset_for_testing = reset
            if not reset_for_testing:
                try:
                    from flask import current_app  # type: ignore
                    reset_for_testing = getattr(current_app, "testing", False)
                except RuntimeError:
                    reset_for_testing = False

            if reset_for_testing:
                self.close_connection()
                if os.path.exists(self.db_path):
                    try:
                        os.remove(self.db_path)
                    except OSError as exc:
                        logger.debug(f"Unable to remove test database file: {exc}")

            if self.connection is None:
                self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row

            # Create tasks table
            self.connection.execute('''
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT,
                    completed BOOLEAN DEFAULT FALSE,
                    priority TEXT DEFAULT 'medium',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Create users table
            self.connection.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    api_key TEXT UNIQUE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            self.connection.commit()
            logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            raise

    def get_connection(self):
        """Get database connection."""
        if not self.connection:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row
        return self.connection


class TaskManager:
    """Manages task operations."""

    def __init__(self, db_manager: Optional[DatabaseManager] = None):
        """Initialize task manager."""
        self.db_manager = db_manager or DatabaseManager()
        self.tasks = []  # In-memory fallback
        self.next_id = 1

    def get_all_tasks(self) -> List[Dict[str, Any]]:
        """Get all tasks from database."""
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.execute('SELECT * FROM tasks ORDER BY created_at DESC')
            tasks = [dict(row) for row in cursor.fetchall()]
            return tasks
        except Exception as e:
            logger.error(f"Error retrieving tasks from database: {e}")
            # Fallback to in-memory storage
            return self.tasks

    def get_task(self, task_id: int) -> Optional[Dict[str, Any]]:
        """Get a specific task by ID."""
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.execute('SELECT * FROM tasks WHERE id = ?', (task_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
        except Exception as e:
            logger.error(f"Error retrieving task {task_id} from database: {e}")
            # Fallback to in-memory storage
            return next((task for task in self.tasks if task['id'] == task_id), None)

    def create_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new task."""
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.execute('''
                INSERT INTO tasks (title, description, completed, priority)
                VALUES (?, ?, ?, ?)
            ''', (
                task_data['title'],
                task_data.get('description', ''),
                task_data.get('completed', False),
                task_data.get('priority', 'medium')
            ))
            task_id = cursor.lastrowid
            conn.commit()

            # Return the created task
            return self.get_task(task_id)
        except Exception as e:
            logger.error(f"Error creating task in database: {e}")
            # Fallback to in-memory storage
            task = {
                'id': self.next_id,
                'title': task_data['title'],
                'description': task_data.get('description', ''),
                'completed': task_data.get('completed', False),
                'priority': task_data.get('priority', 'medium'),
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            self.tasks.append(task)
            self.next_id += 1
            return task

    def update_task(self, task_id: int, task_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update an existing task."""
        try:
            conn = self.db_manager.get_connection()

            # Build dynamic update query
            update_fields = []
            values = []

            for field in ['title', 'description', 'completed', 'priority']:
                if field in task_data:
                    update_fields.append(f"{field} = ?")
                    values.append(task_data[field])

            if not update_fields:
                return self.get_task(task_id)

            values.append(datetime.now().isoformat())  # updated_at
            values.append(task_id)

            query = f'''
                UPDATE tasks
                SET {', '.join(update_fields)}, updated_at = ?
                WHERE id = ?
            '''

            cursor = conn.execute(query, values)
            conn.commit()

            if cursor.rowcount == 0:
                return None

            return self.get_task(task_id)
        except Exception as e:
            logger.error(f"Error updating task {task_id} in database: {e}")
            # Fallback to in-memory storage
            task = self.get_task(task_id)
            if task:
                task.update(task_data)
                task['updated_at'] = datetime.now().isoformat()
            return task

    def delete_task(self, task_id: int) -> bool:
        """Delete a task."""
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Error deleting task {task_id} from database: {e}")
            # Fallback to in-memory storage
            global tasks
            original_length = len(self.tasks)
            self.tasks = [task for task in self.tasks if task['id'] != task_id]
            return len(self.tasks) < original_length


class UserManager:
    """Manages user operations."""

    def __init__(self, db_manager: Optional[DatabaseManager] = None):
        """Initialize user manager."""
        self.db_manager = db_manager or DatabaseManager()
        self.users = []  # In-memory fallback
        self.next_id = 1

    def get_all_users(self) -> List[Dict[str, Any]]:
        """Get all users from database."""
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.execute('SELECT * FROM users ORDER BY created_at DESC')
            users = [dict(row) for row in cursor.fetchall()]
            return users
        except Exception as e:
            logger.error(f"Error retrieving users from database: {e}")
            # Fallback to in-memory storage
            return self.users

    def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get a specific user by ID."""
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
        except Exception as e:
            logger.error(f"Error retrieving user {user_id} from database: {e}")
            # Fallback to in-memory storage
            return next((user for user in self.users if user['id'] == user_id), None)

    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Get a user by username."""
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.execute('SELECT * FROM users WHERE username = ?', (username,))
            row = cursor.fetchone()
            return dict(row) if row else None
        except Exception as e:
            logger.error(f"Error retrieving user by username {username} from database: {e}")
            # Fallback to in-memory storage
            return next((user for user in self.users if user['username'] == username), None)

    def get_user_by_api_key(self, api_key: str) -> Optional[Dict[str, Any]]:
        """Get a user by API key."""
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.execute('SELECT * FROM users WHERE api_key = ?', (api_key,))
            row = cursor.fetchone()
            return dict(row) if row else None
        except Exception as e:
            logger.error(f"Error retrieving user by API key from database: {e}")
            # Fallback to in-memory storage
            return next((user for user in self.users if user['api_key'] == api_key), None)

    def create_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new user."""
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.execute('''
                INSERT INTO users (username, email, api_key)
                VALUES (?, ?, ?)
            ''', (
                user_data['username'],
                user_data['email'],
                user_data['api_key']
            ))
            user_id = cursor.lastrowid
            conn.commit()

            # Return the created user
            return self.get_user(user_id)
        except sqlite3.IntegrityError as e:
            logger.warning(f"Integrity error creating user: {e}")
            raise ValueError("Username or email already exists") from e
        except sqlite3.Error as e:
            logger.error(f"Error creating user in database: {e}")
            # Fallback to in-memory storage
            user = {
                'id': self.next_id,
                'username': user_data['username'],
                'email': user_data['email'],
                'api_key': user_data['api_key'],
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            self.users.append(user)
            self.next_id += 1
            return user

    def update_user(self, user_id: int, user_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update an existing user."""
        try:
            conn = self.db_manager.get_connection()

            # Build dynamic update query
            update_fields = []
            values = []

            for field in ['username', 'email', 'api_key']:
                if field in user_data:
                    update_fields.append(f"{field} = ?")
                    values.append(user_data[field])

            if not update_fields:
                return self.get_user(user_id)

            values.append(datetime.now().isoformat())  # updated_at
            values.append(user_id)

            query = f'''
                UPDATE users
                SET {', '.join(update_fields)}, updated_at = ?
                WHERE id = ?
            '''

            cursor = conn.execute(query, values)
            conn.commit()

            if cursor.rowcount == 0:
                return None

            return self.get_user(user_id)
        except sqlite3.IntegrityError as e:
            logger.warning(f"Integrity error updating user {user_id}: {e}")
            raise ValueError("Username or email already exists") from e
        except sqlite3.Error as e:
            logger.error(f"Error updating user {user_id} in database: {e}")
            # Fallback to in-memory storage
            user = self.get_user(user_id)
            if user:
                user.update(user_data)
                user['updated_at'] = datetime.now().isoformat()
            return user

    def delete_user(self, user_id: int) -> bool:
        """Delete a user."""
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.execute('DELETE FROM users WHERE id = ?', (user_id,))
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Error deleting user {user_id} from database: {e}")
            # Fallback to in-memory storage
            original_length = len(self.users)
            self.users = [user for user in self.users if user['id'] != user_id]
            return len(self.users) < original_length

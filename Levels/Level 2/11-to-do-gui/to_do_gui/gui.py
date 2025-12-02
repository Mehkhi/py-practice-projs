"""
GUI interface for the To-Do application using Tkinter.

This module provides the main window and all GUI components for
interacting with the task management system.
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime
from typing import Optional, List
import logging

from .core import TaskManager, Task


logger = logging.getLogger(__name__)


class TodoGUI:
    """Main GUI application for the To-Do list."""

    def __init__(self, data_file: str = "tasks.json"):
        """Initialize the GUI application."""
        self.task_manager = TaskManager(data_file)
        self.root = tk.Tk()
        self.setup_window()
        self.create_widgets()
        self.refresh_task_list()

        # Bind window close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def setup_window(self):
        """Configure the main window."""
        self.root.title("To-Do List Manager")
        self.root.geometry("800x600")
        self.root.minsize(600, 400)

        # Configure style
        style = ttk.Style()
        style.theme_use('clam')

        # Configure colors for priorities
        style.configure('High.TLabel', foreground='red')
        style.configure('Medium.TLabel', foreground='orange')
        style.configure('Low.TLabel', foreground='green')

    def create_widgets(self):
        """Create and layout all GUI widgets."""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)

        # Title
        title_label = ttk.Label(main_frame, text="To-Do List Manager",
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))

        # Input frame
        input_frame = ttk.LabelFrame(main_frame, text="Add New Task", padding="10")
        input_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        input_frame.columnconfigure(1, weight=1)

        # Task title input
        ttk.Label(input_frame, text="Title:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.title_var = tk.StringVar()
        self.title_entry = ttk.Entry(input_frame, textvariable=self.title_var, width=40)
        self.title_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        self.title_entry.bind('<Return>', lambda e: self.add_task())

        # Priority selection
        ttk.Label(input_frame, text="Priority:").grid(row=0, column=2, sticky=tk.W, padx=(0, 5))
        self.priority_var = tk.StringVar(value="medium")
        priority_combo = ttk.Combobox(input_frame, textvariable=self.priority_var,
                                    values=["low", "medium", "high"], state="readonly", width=10)
        priority_combo.grid(row=0, column=3, padx=(0, 10))

        # Due date input
        ttk.Label(input_frame, text="Due Date:").grid(row=1, column=0, sticky=tk.W, padx=(0, 5), pady=(5, 0))
        self.due_date_var = tk.StringVar()
        self.due_date_entry = ttk.Entry(input_frame, textvariable=self.due_date_var, width=15)
        self.due_date_entry.grid(row=1, column=1, sticky=tk.W, padx=(0, 10), pady=(5, 0))
        self.due_date_entry.insert(0, "YYYY-MM-DD")
        self.due_date_entry.bind('<FocusIn>', self.clear_date_placeholder)

        # Add button
        add_button = ttk.Button(input_frame, text="Add Task", command=self.add_task)
        add_button.grid(row=1, column=2, columnspan=2, pady=(5, 0))

        # Task list frame
        list_frame = ttk.LabelFrame(main_frame, text="Tasks", padding="10")
        list_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(1, weight=1)

        # Search and filter frame
        filter_frame = ttk.Frame(list_frame)
        filter_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        filter_frame.columnconfigure(1, weight=1)

        # Search box
        ttk.Label(filter_frame, text="Search:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.on_search_change)
        search_entry = ttk.Entry(filter_frame, textvariable=self.search_var, width=30)
        search_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))

        # Filter buttons
        filter_buttons_frame = ttk.Frame(filter_frame)
        filter_buttons_frame.grid(row=0, column=2, sticky=tk.E)

        self.filter_var = tk.StringVar(value="all")
        ttk.Radiobutton(filter_buttons_frame, text="All", variable=self.filter_var,
                       value="all", command=self.refresh_task_list).grid(row=0, column=0, padx=(0, 5))
        ttk.Radiobutton(filter_buttons_frame, text="Active", variable=self.filter_var,
                       value="active", command=self.refresh_task_list).grid(row=0, column=1, padx=(0, 5))
        ttk.Radiobutton(filter_buttons_frame, text="Completed", variable=self.filter_var,
                       value="completed", command=self.refresh_task_list).grid(row=0, column=2)

        # Task list with scrollbar
        list_container = ttk.Frame(list_frame)
        list_container.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        list_container.columnconfigure(0, weight=1)
        list_container.rowconfigure(0, weight=1)

        # Treeview for task list
        columns = ('completed', 'title', 'priority', 'due_date', 'created')
        self.task_tree = ttk.Treeview(list_container, columns=columns, show='headings', height=15)

        # Configure columns
        self.task_tree.heading('completed', text='✓')
        self.task_tree.heading('title', text='Title')
        self.task_tree.heading('priority', text='Priority')
        self.task_tree.heading('due_date', text='Due Date')
        self.task_tree.heading('created', text='Created')

        self.task_tree.column('completed', width=50, anchor='center')
        self.task_tree.column('title', width=300, anchor='w')
        self.task_tree.column('priority', width=80, anchor='center')
        self.task_tree.column('due_date', width=100, anchor='center')
        self.task_tree.column('created', width=120, anchor='center')

        # Scrollbar
        scrollbar = ttk.Scrollbar(list_container, orient=tk.VERTICAL, command=self.task_tree.yview)
        self.task_tree.configure(yscrollcommand=scrollbar.set)

        self.task_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

        # Bind double-click event
        self.task_tree.bind('<Double-1>', self.edit_task)

        # Action buttons frame
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.grid(row=3, column=0, columnspan=3, pady=(10, 0))

        # Action buttons
        ttk.Button(buttons_frame, text="Edit Task", command=self.edit_selected_task).grid(row=0, column=0, padx=(0, 5))
        ttk.Button(buttons_frame, text="Delete Task", command=self.delete_selected_task).grid(row=0, column=1, padx=(0, 5))
        ttk.Button(buttons_frame, text="Toggle Complete", command=self.toggle_selected_task).grid(row=0, column=2, padx=(0, 5))
        ttk.Button(buttons_frame, text="Clear Completed", command=self.clear_completed_tasks).grid(row=0, column=3, padx=(0, 5))
        ttk.Button(buttons_frame, text="Statistics", command=self.show_statistics).grid(row=0, column=4)

        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))

    def clear_date_placeholder(self, event):
        """Clear the date placeholder when entry is focused."""
        if self.due_date_entry.get() == "YYYY-MM-DD":
            self.due_date_entry.delete(0, tk.END)

    def add_task(self):
        """Add a new task."""
        title = self.title_var.get().strip()
        if not title:
            messagebox.showwarning("Warning", "Please enter a task title.")
            return

        priority = self.priority_var.get()
        due_date = self.due_date_var.get().strip()

        # Validate due date format
        if due_date and due_date != "YYYY-MM-DD":
            try:
                datetime.strptime(due_date, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("Error", "Please enter due date in YYYY-MM-DD format.")
                return

        try:
            task = self.task_manager.add_task(
                title=title,
                priority=priority,
                due_date=due_date if due_date and due_date != "YYYY-MM-DD" else None
            )
            self.refresh_task_list()
            self.title_var.set("")
            self.due_date_var.set("")
            self.due_date_entry.insert(0, "YYYY-MM-DD")
            self.status_var.set(f"Added task: {title}")
            logger.info(f"Added new task: {title}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add task: {str(e)}")
            logger.error(f"Error adding task: {e}")

    def refresh_task_list(self):
        """Refresh the task list display."""
        # Clear existing items
        for item in self.task_tree.get_children():
            self.task_tree.delete(item)

        # Get tasks based on current filter
        filter_value = self.filter_var.get()
        search_query = self.search_var.get().strip()

        tasks = self.task_manager.get_filtered_tasks(filter_value, search_query)

        # Sort tasks by creation date (newest first)
        tasks.sort(key=lambda t: t.created_at, reverse=True)

        # Add tasks to tree
        for task in tasks:
            completed_text = "✓" if task.completed else ""
            due_date_text = task.due_date if task.due_date else ""
            created_text = datetime.fromisoformat(task.created_at).strftime("%Y-%m-%d")

            # Determine priority color
            priority_style = f"{task.priority.title()}.TLabel"

            item = self.task_tree.insert('', 'end', values=(
                completed_text,
                task.title,
                task.priority.title(),
                due_date_text,
                created_text
            ), tags=(task.id,))

            # Apply priority color
            self.task_tree.set(item, 'priority', task.priority.title())

        # Update status
        self.status_var.set(f"Showing {len(tasks)} task(s)")

    def on_search_change(self, *args):
        """Handle search input changes."""
        self.refresh_task_list()

    def get_selected_task_id(self) -> Optional[str]:
        """Get the ID of the currently selected task."""
        selection = self.task_tree.selection()
        if not selection:
            return None

        item = selection[0]
        tags = self.task_tree.item(item, 'tags')
        return tags[0] if tags else None

    def edit_selected_task(self):
        """Edit the selected task."""
        task_id = self.get_selected_task_id()
        if not task_id:
            messagebox.showwarning("Warning", "Please select a task to edit.")
            return

        self.edit_task_by_id(task_id)

    def edit_task(self, event):
        """Handle double-click to edit task."""
        task_id = self.get_selected_task_id()
        if task_id:
            self.edit_task_by_id(task_id)

    def edit_task_by_id(self, task_id: str):
        """Edit a task by its ID."""
        task = self.task_manager.get_task(task_id)
        if not task:
            messagebox.showerror("Error", "Task not found.")
            return

        # Create edit dialog
        dialog = TaskEditDialog(self.root, task)
        if dialog.result:
            try:
                self.task_manager.update_task(task_id, **dialog.result)
                self.refresh_task_list()
                self.status_var.set(f"Updated task: {dialog.result.get('title', task.title)}")
                logger.info(f"Updated task {task_id}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update task: {str(e)}")
                logger.error(f"Error updating task: {e}")

    def delete_selected_task(self):
        """Delete the selected task."""
        task_id = self.get_selected_task_id()
        if not task_id:
            messagebox.showwarning("Warning", "Please select a task to delete.")
            return

        task = self.task_manager.get_task(task_id)
        if not task:
            messagebox.showerror("Error", "Task not found.")
            return

        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{task.title}'?"):
            try:
                self.task_manager.delete_task(task_id)
                self.refresh_task_list()
                self.status_var.set(f"Deleted task: {task.title}")
                logger.info(f"Deleted task: {task.title}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete task: {str(e)}")
                logger.error(f"Error deleting task: {e}")

    def toggle_selected_task(self):
        """Toggle completion status of selected task."""
        task_id = self.get_selected_task_id()
        if not task_id:
            messagebox.showwarning("Warning", "Please select a task to toggle.")
            return

        try:
            self.task_manager.toggle_task_completion(task_id)
            self.refresh_task_list()
            task = self.task_manager.get_task(task_id)
            status = "completed" if task.completed else "incomplete"
            self.status_var.set(f"Marked task as {status}")
            logger.info(f"Toggled task completion: {task.title}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to toggle task: {str(e)}")
            logger.error(f"Error toggling task: {e}")

    def clear_completed_tasks(self):
        """Clear all completed tasks."""
        completed_count = self.task_manager.get_statistics()["completed"]
        if completed_count == 0:
            messagebox.showinfo("Info", "No completed tasks to clear.")
            return

        if messagebox.askyesno("Confirm Clear", f"Are you sure you want to clear {completed_count} completed task(s)?"):
            try:
                cleared = self.task_manager.clear_completed_tasks()
                self.refresh_task_list()
                self.status_var.set(f"Cleared {cleared} completed task(s)")
                logger.info(f"Cleared {cleared} completed tasks")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to clear completed tasks: {str(e)}")
                logger.error(f"Error clearing completed tasks: {e}")

    def show_statistics(self):
        """Show task statistics."""
        stats = self.task_manager.get_statistics()

        stats_text = f"""Task Statistics:

Total Tasks: {stats['total']}
Completed: {stats['completed']}
Incomplete: {stats['incomplete']}

By Priority:
High: {stats['high_priority']}
Medium: {stats['medium_priority']}
Low: {stats['low_priority']}"""

        messagebox.showinfo("Statistics", stats_text)

    def on_closing(self):
        """Handle window closing event."""
        try:
            self.task_manager.save_tasks()
            logger.info("Application closed, tasks saved")
        except Exception as e:
            logger.error(f"Error saving tasks on close: {e}")
        finally:
            self.root.destroy()

    def run(self):
        """Start the GUI application."""
        logger.info("Starting To-Do GUI application")
        self.root.mainloop()


class TaskEditDialog:
    """Dialog for editing task properties."""

    def __init__(self, parent, task: Task):
        """Initialize the edit dialog."""
        self.result = None

        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Edit Task")
        self.dialog.geometry("400x300")
        self.dialog.transient(parent)
        self.dialog.grab_set()

        # Center the dialog
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))

        self.create_widgets(task)

    def create_widgets(self, task: Task):
        """Create dialog widgets."""
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Title
        ttk.Label(main_frame, text="Title:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        self.title_var = tk.StringVar(value=task.title)
        title_entry = ttk.Entry(main_frame, textvariable=self.title_var, width=40)
        title_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=(0, 5))

        # Description
        ttk.Label(main_frame, text="Description:").grid(row=1, column=0, sticky=tk.W, pady=(0, 5))
        self.description_var = tk.StringVar(value=task.description)
        desc_entry = ttk.Entry(main_frame, textvariable=self.description_var, width=40)
        desc_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=(0, 5))

        # Priority
        ttk.Label(main_frame, text="Priority:").grid(row=2, column=0, sticky=tk.W, pady=(0, 5))
        self.priority_var = tk.StringVar(value=task.priority)
        priority_combo = ttk.Combobox(main_frame, textvariable=self.priority_var,
                                    values=["low", "medium", "high"], state="readonly", width=37)
        priority_combo.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=(0, 5))

        # Due date
        ttk.Label(main_frame, text="Due Date:").grid(row=3, column=0, sticky=tk.W, pady=(0, 5))
        self.due_date_var = tk.StringVar(value=task.due_date or "")
        due_date_entry = ttk.Entry(main_frame, textvariable=self.due_date_var, width=40)
        due_date_entry.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=(0, 20))

        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=(10, 0))

        ttk.Button(button_frame, text="Save", command=self.save_task).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Cancel", command=self.cancel).pack(side=tk.LEFT)

        # Configure grid weights
        main_frame.columnconfigure(1, weight=1)

    def save_task(self):
        """Save the edited task."""
        title = self.title_var.get().strip()
        if not title:
            messagebox.showwarning("Warning", "Please enter a task title.")
            return

        due_date = self.due_date_var.get().strip()
        if due_date:
            try:
                datetime.strptime(due_date, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("Error", "Please enter due date in YYYY-MM-DD format.")
                return

        self.result = {
            "title": title,
            "description": self.description_var.get().strip(),
            "priority": self.priority_var.get(),
            "due_date": due_date if due_date else None
        }

        self.dialog.destroy()

    def cancel(self):
        """Cancel the edit operation."""
        self.dialog.destroy()

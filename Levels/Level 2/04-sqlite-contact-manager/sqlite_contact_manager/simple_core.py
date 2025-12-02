"""
Simplified core contact management functionality with SQLite database.
"""

import sqlite3
import json
import csv
import logging
import os
from typing import List, Dict, Optional, Any, Tuple
from pathlib import Path
from datetime import UTC, datetime

logger = logging.getLogger(__name__)


def _current_timestamp() -> str:
    """Return current UTC timestamp with microsecond precision."""
    return datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S.%f")


class SimpleContactManager:
    """Simplified contact manager without FTS5 to avoid database corruption issues."""

    def __init__(self, db_path: str = "contacts.db"):
        """Initialize contact manager with database path.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self._init_database()

    def _init_database(self) -> None:
        """Initialize database with required tables."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Create contacts table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS contacts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT,
                    phone TEXT,
                    address TEXT,
                    company TEXT,
                    notes TEXT,
                    groups TEXT DEFAULT '[]',
                    custom_fields TEXT DEFAULT '{}',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            conn.commit()
            logger.info("Database initialized successfully")

    def add_contact(self, name: str, email: str = None, phone: str = None,
                   address: str = None, company: str = None, notes: str = None,
                   groups: List[str] = None, custom_fields: Dict[str, Any] = None) -> int:
        """Add a new contact to the database.

        Args:
            name: Contact's full name (required)
            email: Email address
            phone: Phone number
            address: Physical address
            company: Company name
            notes: Additional notes
            groups: List of group names
            custom_fields: Dictionary of custom field values

        Returns:
            ID of the created contact

        Raises:
            ValueError: If name is empty or contact already exists
        """
        if not name or not name.strip():
            raise ValueError("Name is required and cannot be empty")

        # Check for duplicate email
        if email and self._email_exists(email):
            raise ValueError(f"Contact with email '{email}' already exists")

        groups = groups or []
        custom_fields = custom_fields or {}
        timestamp = _current_timestamp()

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO contacts (name, email, phone, address, company, notes, groups, custom_fields, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (name.strip(), email, phone, address, company, notes,
                  json.dumps(groups), json.dumps(custom_fields), timestamp, timestamp))

            contact_id = cursor.lastrowid
            conn.commit()
            logger.info(f"Added contact: {name} (ID: {contact_id})")
            return contact_id

    def get_contact(self, contact_id: int) -> Optional[Dict[str, Any]]:
        """Get a contact by ID.

        Args:
            contact_id: Contact ID

        Returns:
            Contact data dictionary or None if not found
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM contacts WHERE id = ?", (contact_id,))
            row = cursor.fetchone()

            if row:
                return self._row_to_dict(cursor, row)
            return None

    def get_all_contacts(self) -> List[Dict[str, Any]]:
        """Get all contacts from the database.

        Returns:
            List of contact dictionaries
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM contacts ORDER BY name")
            rows = cursor.fetchall()

            return [self._row_to_dict(cursor, row) for row in rows]

    def search_contacts(self, query: str, use_fts: bool = True) -> List[Dict[str, Any]]:
        """Search contacts by query string.

        Args:
            query: Search query
            use_fts: Use full-text search (FTS5) if True, otherwise LIKE search

        Returns:
            List of matching contact dictionaries
        """
        if not query or not query.strip():
            return self.get_all_contacts()

        query = query.strip()

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Always use LIKE search for simplicity
            search_term = f"%{query}%"
            cursor.execute("""
                SELECT * FROM contacts
                WHERE name LIKE ? OR email LIKE ? OR phone LIKE ?
                OR address LIKE ? OR company LIKE ? OR notes LIKE ?
                ORDER BY name
            """, (search_term, search_term, search_term, search_term, search_term, search_term))

            rows = cursor.fetchall()
            return [self._row_to_dict(cursor, row) for row in rows]

    def update_contact(self, contact_id: int, **kwargs) -> bool:
        """Update a contact by ID.

        Args:
            contact_id: Contact ID to update
            **kwargs: Fields to update (name, email, phone, etc.)

        Returns:
            True if contact was updated, False if not found

        Raises:
            ValueError: If email already exists for another contact
        """
        # Check if contact exists
        if not self.get_contact(contact_id):
            return False

        # Check for email conflicts
        if 'email' in kwargs and kwargs['email']:
            existing = self._get_contact_by_email(kwargs['email'])
            if existing and existing['id'] != contact_id:
                raise ValueError(f"Contact with email '{kwargs['email']}' already exists")

        # Prepare update fields
        update_fields = []
        values = []

        for field, value in kwargs.items():
            if field in ['name', 'email', 'phone', 'address', 'company', 'notes']:
                update_fields.append(f"{field} = ?")
                values.append(value)
            elif field == 'groups':
                update_fields.append("groups = ?")
                values.append(json.dumps(value if isinstance(value, list) else []))
            elif field == 'custom_fields':
                update_fields.append("custom_fields = ?")
                values.append(json.dumps(value if isinstance(value, dict) else {}))

        if not update_fields:
            return False

        update_timestamp = _current_timestamp()
        update_fields.append("updated_at = ?")
        values.append(update_timestamp)
        values.append(contact_id)

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(f"""
                UPDATE contacts
                SET {', '.join(update_fields)}
                WHERE id = ?
            """, values)

            conn.commit()
            logger.info(f"Updated contact ID: {contact_id}")
            return cursor.rowcount > 0

    def delete_contact(self, contact_id: int) -> bool:
        """Delete a contact by ID.

        Args:
            contact_id: Contact ID to delete

        Returns:
            True if contact was deleted, False if not found
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM contacts WHERE id = ?", (contact_id,))
            conn.commit()

            if cursor.rowcount > 0:
                logger.info(f"Deleted contact ID: {contact_id}")
                return True
            return False

    def export_to_csv(self, filepath: str) -> None:
        """Export all contacts to CSV file.

        Args:
            filepath: Path to output CSV file
        """
        contacts = self.get_all_contacts()

        if not contacts:
            logger.warning("No contacts to export")
            return

        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['id', 'name', 'email', 'phone', 'address', 'company', 'notes', 'groups', 'custom_fields', 'created_at', 'updated_at']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for contact in contacts:
                # Convert JSON fields to strings for CSV
                contact_copy = contact.copy()
                contact_copy['groups'] = json.dumps(contact['groups'])
                contact_copy['custom_fields'] = json.dumps(contact['custom_fields'])
                writer.writerow(contact_copy)

        logger.info(f"Exported {len(contacts)} contacts to {filepath}")

    def import_from_csv(self, filepath: str, skip_duplicates: bool = True) -> Tuple[int, int]:
        """Import contacts from CSV file.

        Args:
            filepath: Path to input CSV file
            skip_duplicates: Skip contacts with duplicate emails

        Returns:
            Tuple of (imported_count, skipped_count)
        """
        if not Path(filepath).exists():
            raise FileNotFoundError(f"CSV file not found: {filepath}")

        imported = 0
        skipped = 0

        with open(filepath, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)

            for row in reader:
                try:
                    # Parse JSON fields
                    groups = json.loads(row.get('groups', '[]'))
                    custom_fields = json.loads(row.get('custom_fields', '{}'))

                    # Check for duplicates
                    if skip_duplicates and row.get('email') and self._email_exists(row['email']):
                        skipped += 1
                        logger.warning(f"Skipped duplicate email: {row['email']}")
                        continue

                    self.add_contact(
                        name=row['name'],
                        email=row.get('email'),
                        phone=row.get('phone'),
                        address=row.get('address'),
                        company=row.get('company'),
                        notes=row.get('notes'),
                        groups=groups,
                        custom_fields=custom_fields
                    )
                    imported += 1

                except Exception as e:
                    logger.error(f"Error importing contact {row.get('name', 'Unknown')}: {e}")
                    skipped += 1

        logger.info(f"Import complete: {imported} imported, {skipped} skipped")
        return imported, skipped

    def get_contact_groups(self) -> List[str]:
        """Get all unique contact groups.

        Returns:
            List of unique group names
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT groups FROM contacts WHERE groups != '[]'")
            rows = cursor.fetchall()

            all_groups = set()
            for row in rows:
                groups = json.loads(row[0])
                all_groups.update(groups)

            return sorted(list(all_groups))

    def get_contacts_by_group(self, group_name: str) -> List[Dict[str, Any]]:
        """Get all contacts in a specific group.

        Args:
            group_name: Name of the group

        Returns:
            List of contact dictionaries in the group
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM contacts
                WHERE groups LIKE ?
                ORDER BY name
            """, (f'%"{group_name}"%',))

            rows = cursor.fetchall()
            return [self._row_to_dict(cursor, row) for row in rows]

    def _email_exists(self, email: str) -> bool:
        """Check if email already exists in database.

        Args:
            email: Email to check

        Returns:
            True if email exists, False otherwise
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM contacts WHERE email = ?", (email,))
            return cursor.fetchone() is not None

    def _get_contact_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get contact by email address.

        Args:
            email: Email address to search for

        Returns:
            Contact dictionary or None if not found
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM contacts WHERE email = ?", (email,))
            row = cursor.fetchone()

            if row:
                return self._row_to_dict(cursor, row)
            return None

    def _row_to_dict(self, cursor: sqlite3.Cursor, row: Tuple) -> Dict[str, Any]:
        """Convert database row to dictionary.

        Args:
            cursor: Database cursor
            row: Database row tuple

        Returns:
            Dictionary representation of the contact
        """
        columns = [description[0] for description in cursor.description]
        contact = dict(zip(columns, row))

        # Parse JSON fields
        contact['groups'] = json.loads(contact['groups'])
        contact['custom_fields'] = json.loads(contact['custom_fields'])

        return contact

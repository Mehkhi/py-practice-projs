#!/usr/bin/env python3

import unittest
import os
import tempfile
from address_book import AddressBook


class TestAddressBook(unittest.TestCase):

    def setUp(self):
        """Set up test fixtures."""
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        self.temp_filename = self.temp_file.name
        self.temp_file.close()
        self.address_book = AddressBook(self.temp_filename)

    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.temp_filename):
            os.unlink(self.temp_filename)

    def test_add_contact(self):
        """Test adding a new contact."""
        result = self.address_book.add_contact("John Doe", "555-123-4567", "john@example.com", "123 Main St")
        self.assertTrue(result)
        self.assertEqual(len(self.address_book.contacts), 1)

        contact = self.address_book.contacts[0]
        self.assertEqual(contact["name"], "John Doe")
        self.assertEqual(contact["phone"], "(555) 123-4567")
        self.assertEqual(contact["email"], "john@example.com")
        self.assertEqual(contact["address"], "123 Main St")

    def test_add_empty_name(self):
        """Test adding a contact with empty name."""
        result = self.address_book.add_contact("", "555-123-4567", "john@example.com")
        self.assertFalse(result)
        self.assertEqual(len(self.address_book.contacts), 0)

    def test_validate_email(self):
        """Test email validation."""
        # Valid emails
        self.assertTrue(self.address_book.validate_email("test@example.com"))
        self.assertTrue(self.address_book.validate_email("user.name+tag@domain.co.uk"))

        # Invalid emails
        self.assertFalse(self.address_book.validate_email("invalid-email"))
        self.assertFalse(self.address_book.validate_email("@domain.com"))
        self.assertFalse(self.address_book.validate_email("user@"))
        self.assertFalse(self.address_book.validate_email(""))

    def test_validate_phone(self):
        """Test phone validation."""
        # Valid phones
        self.assertTrue(self.address_book.validate_phone("555-123-4567"))
        self.assertTrue(self.address_book.validate_phone("(555) 123-4567"))
        self.assertTrue(self.address_book.validate_phone("5551234567"))
        self.assertTrue(self.address_book.validate_phone("1-555-123-4567"))

        # Invalid phones
        self.assertFalse(self.address_book.validate_phone("123"))
        self.assertFalse(self.address_book.validate_phone(""))
        self.assertFalse(self.address_book.validate_phone("abc-def-ghij"))

    def test_format_phone(self):
        """Test phone formatting."""
        # 10-digit numbers
        self.assertEqual(self.address_book.format_phone("5551234567"), "(555) 123-4567")
        self.assertEqual(self.address_book.format_phone("555-123-4567"), "(555) 123-4567")
        self.assertEqual(self.address_book.format_phone("(555) 123-4567"), "(555) 123-4567")

        # 11-digit numbers (with country code)
        self.assertEqual(self.address_book.format_phone("15551234567"), "+1 (555) 123-4567")

        # Invalid numbers (return as-is)
        self.assertEqual(self.address_book.format_phone("123"), "123")
        self.assertEqual(self.address_book.format_phone("invalid"), "invalid")

    def test_update_contact(self):
        """Test updating a contact."""
        self.address_book.add_contact("John Doe", "555-123-4567", "john@example.com")
        contact_id = self.address_book.contacts[0]["id"]

        result = self.address_book.update_contact(
            contact_id,
            name="John Smith",
            phone="555-987-6543",
            email="john.smith@example.com"
        )
        self.assertTrue(result)

        contact = self.address_book.contacts[0]
        self.assertEqual(contact["name"], "John Smith")
        self.assertEqual(contact["phone"], "(555) 987-6543")
        self.assertEqual(contact["email"], "john.smith@example.com")

    def test_update_nonexistent_contact(self):
        """Test updating a non-existent contact."""
        result = self.address_book.update_contact(999, name="New Name")
        self.assertFalse(result)

    def test_delete_contact(self):
        """Test deleting a contact."""
        self.address_book.add_contact("John Doe", "555-123-4567")
        contact_id = self.address_book.contacts[0]["id"]

        result = self.address_book.delete_contact(contact_id)
        self.assertTrue(result)
        self.assertEqual(len(self.address_book.contacts), 0)

    def test_delete_nonexistent_contact(self):
        """Test deleting a non-existent contact."""
        result = self.address_book.delete_contact(999)
        self.assertFalse(result)

    def test_search_contacts(self):
        """Test searching contacts."""
        self.address_book.add_contact("John Doe", "555-123-4567", "john@example.com")
        self.address_book.add_contact("Jane Smith", "555-987-6543", "jane@example.com")
        self.address_book.add_contact("Bob Johnson", "555-555-5555", "bob@johnson.com")

        # Search by name
        results = self.address_book.search_contacts("john")
        self.assertEqual(len(results), 2)  # John Doe and Bob Johnson

        # Search by phone (digits only)
        results = self.address_book.search_contacts("5555555555")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["name"], "Bob Johnson")

    def test_get_stats(self):
        """Test getting address book statistics."""
        # Empty address book
        stats = self.address_book.get_stats()
        self.assertEqual(stats["total"], 0)
        self.assertEqual(stats["with_phone"], 0)
        self.assertEqual(stats["with_email"], 0)
        self.assertEqual(stats["with_address"], 0)

        # Add contacts
        self.address_book.add_contact("John Doe", "555-123-4567", "john@example.com", "123 Main St")
        self.address_book.add_contact("Jane Smith", "555-987-6543", "", "")
        self.address_book.add_contact("Bob Johnson", "", "bob@johnson.com", "")

        stats = self.address_book.get_stats()
        self.assertEqual(stats["total"], 3)
        self.assertEqual(stats["with_phone"], 2)
        self.assertEqual(stats["with_email"], 2)
        self.assertEqual(stats["with_address"], 1)

    def test_save_load_contacts(self):
        """Test saving and loading contacts."""
        # Add contacts
        self.address_book.add_contact("John Doe", "555-123-4567", "john@example.com", "123 Main St")
        self.address_book.add_contact("Jane Smith", "555-987-6543", "jane@example.com")

        # Create new instance to load from file
        new_address_book = AddressBook(self.temp_filename)

        self.assertEqual(len(new_address_book.contacts), 2)
        self.assertEqual(new_address_book.contacts[0]["name"], "John Doe")
        self.assertEqual(new_address_book.contacts[0]["phone"], "(555) 123-4567")
        self.assertEqual(new_address_book.contacts[0]["email"], "john@example.com")
        self.assertEqual(new_address_book.contacts[0]["address"], "123 Main St")

        self.assertEqual(new_address_book.contacts[1]["name"], "Jane Smith")
        self.assertEqual(new_address_book.contacts[1]["phone"], "(555) 987-6543")
        self.assertEqual(new_address_book.contacts[1]["email"], "jane@example.com")


if __name__ == "__main__":
    unittest.main()

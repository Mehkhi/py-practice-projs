#!/usr/bin/env python3

import json
import os
import re
from typing import List, Dict, Any, Optional


class AddressBook:
    """A simple address book manager with JSON persistence."""

    def __init__(self, filename="contacts.json"):
        self.filename = filename
        self.contacts = []
        self.load_contacts()

    def load_contacts(self):
        """Load contacts from JSON file."""
        try:
            if os.path.exists(self.filename):
                with open(self.filename, 'r', encoding='utf-8') as file:
                    self.contacts = json.load(file)
            else:
                self.contacts = []
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading contacts: {e}")
            self.contacts = []

    def save_contacts(self):
        """Save contacts to JSON file."""
        try:
            with open(self.filename, 'w', encoding='utf-8') as file:
                json.dump(self.contacts, file, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"Error saving contacts: {e}")

    def validate_email(self, email: str) -> bool:
        """Basic email validation."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    def validate_phone(self, phone: str) -> bool:
        """Basic phone number validation."""
        # Remove all non-digit characters
        digits_only = re.sub(r'\D', '', phone)
        return len(digits_only) >= 10

    def format_phone(self, phone: str) -> str:
        """Format phone number to standard format."""
        digits_only = re.sub(r'\D', '', phone)

        if len(digits_only) == 10:
            return f"({digits_only[:3]}) {digits_only[3:6]}-{digits_only[6:]}"
        elif len(digits_only) == 11 and digits_only[0] == '1':
            return f"+1 ({digits_only[1:4]}) {digits_only[4:7]}-{digits_only[7:]}"
        else:
            return phone  # Return original if can't format

    def add_contact(self, name: str, phone: str, email: str = "", address: str = "") -> bool:
        """Add a new contact."""
        if not name.strip():
            return False

        # Validate phone number
        if phone and not self.validate_phone(phone):
            print("Warning: Phone number format may be invalid")

        # Validate email
        if email and not self.validate_email(email):
            print("Warning: Email format may be invalid")

        contact = {
            "id": len(self.contacts) + 1,
            "name": name.strip(),
            "phone": self.format_phone(phone) if phone else "",
            "email": email.strip() if email else "",
            "address": address.strip() if address else ""
        }

        self.contacts.append(contact)
        self.save_contacts()
        return True

    def find_contact_by_id(self, contact_id: int) -> Optional[Dict[str, Any]]:
        """Find a contact by ID."""
        for contact in self.contacts:
            if contact["id"] == contact_id:
                return contact
        return None

    def update_contact(self, contact_id: int, name: str = None, phone: str = None,
                      email: str = None, address: str = None) -> bool:
        """Update an existing contact."""
        contact = self.find_contact_by_id(contact_id)
        if not contact:
            return False

        if name is not None:
            if not name.strip():
                return False
            contact["name"] = name.strip()

        if phone is not None:
            if phone and not self.validate_phone(phone):
                print("Warning: Phone number format may be invalid")
            contact["phone"] = self.format_phone(phone) if phone else ""

        if email is not None:
            if email and not self.validate_email(email):
                print("Warning: Email format may be invalid")
            contact["email"] = email.strip() if email else ""

        if address is not None:
            contact["address"] = address.strip() if address else ""

        self.save_contacts()
        return True

    def delete_contact(self, contact_id: int) -> bool:
        """Delete a contact."""
        for i, contact in enumerate(self.contacts):
            if contact["id"] == contact_id:
                del self.contacts[i]
                self.save_contacts()
                return True
        return False

    def search_contacts(self, query: str) -> List[Dict[str, Any]]:
        """Search contacts by name."""
        query = query.lower()
        results = []

        for contact in self.contacts:
            if (query in contact["name"].lower() or
                query in contact["email"].lower() or
                query in contact["phone"].replace(" ", "").replace("-", "").replace("(", "").replace(")", "") or
                query in contact["address"].lower()):
                results.append(contact)

        return results

    def get_all_contacts(self) -> List[Dict[str, Any]]:
        """Get all contacts."""
        return self.contacts

    def get_stats(self) -> Dict[str, int]:
        """Get address book statistics."""
        return {
            "total": len(self.contacts),
            "with_phone": len([c for c in self.contacts if c["phone"]]),
            "with_email": len([c for c in self.contacts if c["email"]]),
            "with_address": len([c for c in self.contacts if c["address"]])
        }


def display_contacts(contacts: List[Dict[str, Any]], show_numbers: bool = True):
    """Display a list of contacts in a formatted way."""
    if not contacts:
        print("No contacts found.")
        return

    print("\n" + "="*60)
    print("[CARD INDEX] ADDRESS BOOK")
    print("="*60)

    for i, contact in enumerate(contacts, 1):
        if show_numbers:
            print(f"{i:2d}. {contact['name']}")
        else:
            print(f"    {contact['name']}")

        if contact["phone"]:
            print(f"    [PHONE] {contact['phone']}")
        if contact["email"]:
            print(f"    [EMAIL] {contact['email']}")
        if contact["address"]:
            print(f"    [HOUSE] {contact['address']}")
        print()

    print("="*60)


def get_user_input(prompt: str, allow_empty: bool = False) -> str:
    """Get and validate user input."""
    while True:
        try:
            user_input = input(prompt).strip()
            if user_input or allow_empty:
                return user_input
            else:
                print("Please enter some text.")
        except KeyboardInterrupt:
            print("\nGoodbye!")
            exit()
        except EOFError:
            print("\nGoodbye!")
            exit()


def get_contact_id(address_book: AddressBook, prompt: str) -> int:
    """Get a valid contact ID from user."""
    while True:
        try:
            contact_id = int(input(prompt))
            if 1 <= contact_id <= len(address_book.contacts):
                return contact_id
            else:
                print(f"Please enter a number between 1 and {len(address_book.contacts)}.")
        except ValueError:
            print("Please enter a valid number.")
        except KeyboardInterrupt:
            print("\nGoodbye!")
            exit()
        except EOFError:
            print("\nGoodbye!")
            exit()


def add_contact_menu(address_book: AddressBook):
    """Handle adding a new contact."""
    print("\n=== Add New Contact ===")

    name = get_user_input("Enter name: ")
    phone = get_user_input("Enter phone number: ", allow_empty=True)
    email = get_user_input("Enter email: ", allow_empty=True)
    address = get_user_input("Enter address: ", allow_empty=True)

    if address_book.add_contact(name, phone, email, address):
        print(f"[OK] Contact added: {name}")
    else:
        print("[X] Failed to add contact.")


def list_contacts_menu(address_book: AddressBook):
    """Handle listing contacts."""
    print("\n=== List Contacts ===")
    contacts = address_book.get_all_contacts()
    display_contacts(contacts)


def search_contacts_menu(address_book: AddressBook):
    """Handle searching contacts."""
    print("\n=== Search Contacts ===")
    query = get_user_input("Enter search term: ")

    if not query:
        print("Please enter a search term.")
        return

    results = address_book.search_contacts(query)

    if results:
        print(f"\nFound {len(results)} contact(s):")
        display_contacts(results, show_numbers=False)
    else:
        print("No contacts found.")


def edit_contact_menu(address_book: AddressBook):
    """Handle editing a contact."""
    if not address_book.contacts:
        print("\nNo contacts to edit!")
        return

    print("\n=== Edit Contact ===")
    display_contacts(address_book.contacts)

    contact_id = get_contact_id(address_book, "Enter contact number to edit: ")
    contact = address_book.find_contact_by_id(contact_id)

    if not contact:
        print("[X] Contact not found.")
        return

    print(f"\nEditing: {contact['name']}")
    print("Leave blank to keep current value")

    name = get_user_input(f"Name [{contact['name']}]: ", allow_empty=True)
    phone = get_user_input(f"Phone [{contact['phone']}]: ", allow_empty=True)
    email = get_user_input(f"Email [{contact['email']}]: ", allow_empty=True)
    address = get_user_input(f"Address [{contact['address']}]: ", allow_empty=True)

    # Only update fields that were changed
    updates = {}
    if name:
        updates["name"] = name
    if phone != contact["phone"]:
        updates["phone"] = phone
    if email != contact["email"]:
        updates["email"] = email
    if address != contact["address"]:
        updates["address"] = address

    if updates:
        if address_book.update_contact(contact_id, **updates):
            print("[OK] Contact updated successfully.")
        else:
            print("[X] Failed to update contact.")
    else:
        print("No changes made.")


def delete_contact_menu(address_book: AddressBook):
    """Handle deleting a contact."""
    if not address_book.contacts:
        print("\nNo contacts to delete!")
        return

    print("\n=== Delete Contact ===")
    display_contacts(address_book.contacts)

    contact_id = get_contact_id(address_book, "Enter contact number to delete: ")
    contact = address_book.find_contact_by_id(contact_id)

    if not contact:
        print("[X] Contact not found.")
        return

    confirm = input(f"Delete '{contact['name']}'? (y/n): ").strip().lower()
    if confirm in ['y', 'yes']:
        if address_book.delete_contact(contact_id):
            print("[OK] Contact deleted successfully.")
        else:
            print("[X] Failed to delete contact.")
    else:
        print("Cancelled.")


def show_stats(address_book: AddressBook):
    """Display address book statistics."""
    stats = address_book.get_stats()

    print("\n" + "="*40)
    print("[BAR CHART] ADDRESS BOOK STATISTICS")
    print("="*40)
    print(f"Total contacts:     {stats['total']}")
    print(f"With phone:         {stats['with_phone']}")
    print(f"With email:         {stats['with_email']}")
    print(f"With address:       {stats['with_address']}")
    print("="*40)


def export_to_csv(address_book: AddressBook):
    """Export contacts to CSV file."""
    if not address_book.contacts:
        print("\nNo contacts to export!")
        return

    filename = get_user_input("Enter CSV filename (default: contacts.csv): ") or "contacts.csv"

    if not filename.endswith('.csv'):
        filename += '.csv'

    try:
        with open(filename, 'w', encoding='utf-8') as file:
            file.write("Name,Phone,Email,Address\n")
            for contact in address_book.contacts:
                # Escape commas and quotes in fields
                name = f'"{contact["name"].replace('"', '""')}"'
                phone = f'"{contact["phone"]}"'
                email = f'"{contact["email"]}"'
                address = f'"{contact["address"].replace('"', '""')}"'
                file.write(f"{name},{phone},{email},{address}\n")

        print(f"[OK] Contacts exported to {filename}")
    except IOError as e:
        print(f"[X] Error exporting contacts: {e}")


def display_menu():
    """Display the main menu."""
    print("\n" + "="*40)
    print("[CARD INDEX] ADDRESS BOOK MANAGER")
    print("="*40)
    print("1. Add new contact")
    print("2. List all contacts")
    print("3. Search contacts")
    print("4. Edit contact")
    print("5. Delete contact")
    print("6. Show statistics")
    print("7. Export to CSV")
    print("8. Exit")
    print("="*40)


def main():
    """Main function to run the address book manager."""
    address_book = AddressBook()

    print("Welcome to the Address Book Manager!")

    while True:
        display_menu()

        try:
            choice = input("Enter your choice (1-8): ").strip()

            if choice == '1':
                add_contact_menu(address_book)
            elif choice == '2':
                list_contacts_menu(address_book)
            elif choice == '3':
                search_contacts_menu(address_book)
            elif choice == '4':
                edit_contact_menu(address_book)
            elif choice == '5':
                delete_contact_menu(address_book)
            elif choice == '6':
                show_stats(address_book)
            elif choice == '7':
                export_to_csv(address_book)
            elif choice == '8':
                print("Goodbye!")
                break
            else:
                print("Invalid choice. Please enter 1-8.")

        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except EOFError:
            print("\nGoodbye!")
            break


if __name__ == "__main__":
    main()

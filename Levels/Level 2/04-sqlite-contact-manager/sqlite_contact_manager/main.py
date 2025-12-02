"""
Command-line interface for SQLite Contact Manager.
"""

import argparse
import sys
import logging
from typing import List, Dict, Any
from pathlib import Path

from .core import ContactManager


def setup_logging(verbose: bool = False) -> None:
    """Setup logging configuration.

    Args:
        verbose: Enable verbose logging
    """
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler()]
    )


def print_contact(contact: Dict[str, Any]) -> None:
    """Print a single contact in a formatted way.

    Args:
        contact: Contact dictionary
    """
    print(f"\nID: {contact['id']}")
    print(f"Name: {contact['name']}")
    if contact['email']:
        print(f"Email: {contact['email']}")
    if contact['phone']:
        print(f"Phone: {contact['phone']}")
    if contact['address']:
        print(f"Address: {contact['address']}")
    if contact['company']:
        print(f"Company: {contact['company']}")
    if contact['notes']:
        print(f"Notes: {contact['notes']}")
    if contact['groups']:
        print(f"Groups: {', '.join(contact['groups'])}")
    if contact['custom_fields']:
        print("Custom Fields:")
        for key, value in contact['custom_fields'].items():
            print(f"  {key}: {value}")
    print(f"Created: {contact['created_at']}")
    print(f"Updated: {contact['updated_at']}")


def print_contacts(contacts: List[Dict[str, Any]], show_details: bool = False) -> None:
    """Print a list of contacts.

    Args:
        contacts: List of contact dictionaries
        show_details: Show full details for each contact
    """
    if not contacts:
        print("No contacts found.")
        return

    if show_details:
        for contact in contacts:
            print_contact(contact)
            print("-" * 50)
    else:
        print(f"\nFound {len(contacts)} contact(s):")
        print("-" * 80)
        print(f"{'ID':<5} {'Name':<25} {'Email':<30} {'Phone':<15}")
        print("-" * 80)
        for contact in contacts:
            print(f"{contact['id']:<5} {contact['name']:<25} {contact['email'] or '':<30} {contact['phone'] or '':<15}")


def add_contact(args, manager: ContactManager) -> None:
    """Add a new contact.

    Args:
        args: Parsed command line arguments
        manager: ContactManager instance
    """
    try:
        contact_id = manager.add_contact(
            name=args.name,
            email=args.email,
            phone=args.phone,
            address=args.address,
            company=args.company,
            notes=args.notes,
            groups=args.groups.split(',') if args.groups else [],
            custom_fields=args.custom_fields or {}
        )
        print(f"Contact added successfully with ID: {contact_id}")
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)


def get_contact(args, manager: ContactManager) -> None:
    """Get a contact by ID.

    Args:
        args: Parsed command line arguments
        manager: ContactManager instance
    """
    contact = manager.get_contact(args.id)
    if contact:
        print_contact(contact)
    else:
        print(f"Contact with ID {args.id} not found.")


def list_contacts(args, manager: ContactManager) -> None:
    """List all contacts.

    Args:
        args: Parsed command line arguments
        manager: ContactManager instance
    """
    contacts = manager.get_all_contacts()
    print_contacts(contacts, args.details)


def search_contacts(args, manager: ContactManager) -> None:
    """Search contacts.

    Args:
        args: Parsed command line arguments
        manager: ContactManager instance
    """
    contacts = manager.search_contacts(args.query, use_fts=not args.no_fts)
    print_contacts(contacts, args.details)


def update_contact(args, manager: ContactManager) -> None:
    """Update a contact.

    Args:
        args: Parsed command line arguments
        manager: ContactManager instance
    """
    # Build update dictionary from provided arguments
    update_data = {}
    if args.name:
        update_data['name'] = args.name
    if args.email:
        update_data['email'] = args.email
    if args.phone:
        update_data['phone'] = args.phone
    if args.address:
        update_data['address'] = args.address
    if args.company:
        update_data['company'] = args.company
    if args.notes:
        update_data['notes'] = args.notes
    if args.groups:
        update_data['groups'] = args.groups.split(',')
    if args.custom_fields:
        update_data['custom_fields'] = args.custom_fields

    if not update_data:
        print("No fields to update. Provide at least one field to update.")
        return

    try:
        if manager.update_contact(args.id, **update_data):
            print(f"Contact {args.id} updated successfully.")
        else:
            print(f"Contact with ID {args.id} not found.")
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)


def delete_contact(args, manager: ContactManager) -> None:
    """Delete a contact.

    Args:
        args: Parsed command line arguments
        manager: ContactManager instance
    """
    if manager.delete_contact(args.id):
        print(f"Contact {args.id} deleted successfully.")
    else:
        print(f"Contact with ID {args.id} not found.")


def export_contacts(args, manager: ContactManager) -> None:
    """Export contacts to CSV.

    Args:
        args: Parsed command line arguments
        manager: ContactManager instance
    """
    try:
        manager.export_to_csv(args.file)
        print(f"Contacts exported to {args.file}")
    except Exception as e:
        print(f"Error exporting contacts: {e}")
        sys.exit(1)


def import_contacts(args, manager: ContactManager) -> None:
    """Import contacts from CSV.

    Args:
        args: Parsed command line arguments
        manager: ContactManager instance
    """
    try:
        imported, skipped = manager.import_from_csv(args.file, skip_duplicates=not args.overwrite)
        print(f"Import complete: {imported} imported, {skipped} skipped")
    except Exception as e:
        print(f"Error importing contacts: {e}")
        sys.exit(1)


def list_groups(args, manager: ContactManager) -> None:
    """List all contact groups.

    Args:
        args: Parsed command line arguments
        manager: ContactManager instance
    """
    groups = manager.get_contact_groups()
    if groups:
        print("Contact Groups:")
        for group in groups:
            print(f"  - {group}")
    else:
        print("No groups found.")


def get_group_contacts(args, manager: ContactManager) -> None:
    """Get contacts in a specific group.

    Args:
        args: Parsed command line arguments
        manager: ContactManager instance
    """
    contacts = manager.get_contacts_by_group(args.group)
    print_contacts(contacts, args.details)


def create_parser() -> argparse.ArgumentParser:
    """Create command line argument parser.

    Returns:
        Configured ArgumentParser instance
    """
    parser = argparse.ArgumentParser(
        description="SQLite Contact Manager - A professional CLI tool for managing contacts",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s add --name "John Doe" --email "john@example.com" --phone "555-1234"
  %(prog)s get --id 1
  %(prog)s list --details
  %(prog)s search "john" --details
  %(prog)s update --id 1 --phone "555-5678"
  %(prog)s delete --id 1
  %(prog)s export --file contacts.csv
  %(prog)s import --file contacts.csv
  %(prog)s groups
  %(prog)s group-contacts --group "work"
        """
    )

    parser.add_argument('--db', default='contacts.db', help='Database file path (default: contacts.db)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose logging')

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Add contact command
    add_parser = subparsers.add_parser('add', help='Add a new contact')
    add_parser.add_argument('--name', required=True, help='Contact name')
    add_parser.add_argument('--email', help='Email address')
    add_parser.add_argument('--phone', help='Phone number')
    add_parser.add_argument('--address', help='Physical address')
    add_parser.add_argument('--company', help='Company name')
    add_parser.add_argument('--notes', help='Additional notes')
    add_parser.add_argument('--groups', help='Comma-separated list of groups')
    add_parser.add_argument('--custom-fields', type=dict, help='Custom fields as JSON')

    # Get contact command
    get_parser = subparsers.add_parser('get', help='Get a contact by ID')
    get_parser.add_argument('--id', type=int, required=True, help='Contact ID')

    # List contacts command
    list_parser = subparsers.add_parser('list', help='List all contacts')
    list_parser.add_argument('--details', action='store_true', help='Show detailed information')

    # Search contacts command
    search_parser = subparsers.add_parser('search', help='Search contacts')
    search_parser.add_argument('query', help='Search query')
    search_parser.add_argument('--details', action='store_true', help='Show detailed information')
    search_parser.add_argument('--no-fts', action='store_true', help='Use LIKE search instead of FTS5')

    # Update contact command
    update_parser = subparsers.add_parser('update', help='Update a contact')
    update_parser.add_argument('--id', type=int, required=True, help='Contact ID to update')
    update_parser.add_argument('--name', help='New name')
    update_parser.add_argument('--email', help='New email')
    update_parser.add_argument('--phone', help='New phone')
    update_parser.add_argument('--address', help='New address')
    update_parser.add_argument('--company', help='New company')
    update_parser.add_argument('--notes', help='New notes')
    update_parser.add_argument('--groups', help='New groups (comma-separated)')
    update_parser.add_argument('--custom-fields', type=dict, help='New custom fields as JSON')

    # Delete contact command
    delete_parser = subparsers.add_parser('delete', help='Delete a contact')
    delete_parser.add_argument('--id', type=int, required=True, help='Contact ID to delete')

    # Export contacts command
    export_parser = subparsers.add_parser('export', help='Export contacts to CSV')
    export_parser.add_argument('--file', required=True, help='Output CSV file path')

    # Import contacts command
    import_parser = subparsers.add_parser('import', help='Import contacts from CSV')
    import_parser.add_argument('--file', required=True, help='Input CSV file path')
    import_parser.add_argument('--overwrite', action='store_true', help='Overwrite duplicate contacts')

    # List groups command
    groups_parser = subparsers.add_parser('groups', help='List all contact groups')

    # Get group contacts command
    group_contacts_parser = subparsers.add_parser('group-contacts', help='Get contacts in a group')
    group_contacts_parser.add_argument('--group', required=True, help='Group name')
    group_contacts_parser.add_argument('--details', action='store_true', help='Show detailed information')

    return parser


def main() -> None:
    """Main entry point for the CLI application."""
    parser = create_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    setup_logging(args.verbose)

    try:
        manager = ContactManager(args.db)

        # Route to appropriate command handler
        command_handlers = {
            'add': add_contact,
            'get': get_contact,
            'list': list_contacts,
            'search': search_contacts,
            'update': update_contact,
            'delete': delete_contact,
            'export': export_contacts,
            'import': import_contacts,
            'groups': list_groups,
            'group-contacts': get_group_contacts,
        }

        handler = command_handlers.get(args.command)
        if handler:
            handler(args, manager)
        else:
            print(f"Unknown command: {args.command}")
            sys.exit(1)

    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()

# Address Book Manager

A command-line address book application with contact management, search functionality, and data persistence.

## What It Does

This program provides a complete contact management system that:
- Add, edit, and delete contacts
- Search contacts by name, phone, email, or address
- List all contacts with detailed information
- Validate and format phone numbers and emails
- Save contacts to JSON file
- Export contacts to CSV format
- Display address book statistics

## How to Run

1. Make sure you have Python 3.7 or higher installed
2. Run the program:
   ```bash
   python address_book.py
   ```
3. Follow the menu prompts to manage your contacts

## Example Usage

### Adding a Contact
```
[CARD INDEX] ADDRESS BOOK MANAGER
========================================
1. Add new contact
2. List all contacts
3. Search contacts
4. Edit contact
5. Delete contact
6. Show statistics
7. Export to CSV
8. Exit
========================================
Enter your choice (1-8): 1

=== Add New Contact ===
Enter name: John Doe
Enter phone number: 555-123-4567
Enter email: john@example.com
Enter address: 123 Main St, Anytown, USA
[OK] Contact added: John Doe
```

### Listing Contacts
```
=== List Contacts ===

============================================================
[CARD INDEX] ADDRESS BOOK
============================================================
 1. John Doe
    [PHONE] (555) 123-4567
    [EMAIL] john@example.com
    [HOUSE] 123 Main St, Anytown, USA

 2. Jane Smith
    [PHONE] (555) 987-6543
    [EMAIL] jane.smith@example.com

============================================================
```

### Searching Contacts
```
=== Search Contacts ===
Enter search term: john

Found 1 contact(s):

============================================================
[CARD INDEX] ADDRESS BOOK
============================================================
    John Doe
    [PHONE] (555) 123-4567
    [EMAIL] john@example.com
    [HOUSE] 123 Main St, Anytown, USA

============================================================
```

## Features

### Core Features
- **Contact Management**: Add, edit, delete contacts with full details
- **Search**: Find contacts by name, phone, email, or address
- **Validation**: Automatic phone number and email validation
- **Formatting**: Standardized phone number formatting
- **Persistence**: Automatic saving to JSON file
- **Export**: Export contacts to CSV format
- **Statistics**: Track contact counts and data completeness

### Data Validation
- **Phone Numbers**: Validates 10-digit US numbers and formats as (XXX) XXX-XXXX
- **Email Addresses**: Basic email format validation
- **Required Fields**: Name is required for all contacts

### User Interface
- **Interactive Menu**: Easy-to-navigate command-line interface
- **Visual Indicators**: Emojis for different contact fields
- **Formatted Display**: Clean, readable contact listings
- **Error Handling**: Graceful handling of invalid input

## Data Storage

Contacts are automatically saved to `contacts.json` in the same directory as the script. Each contact contains:

```json
{
  "id": 1,
  "name": "John Doe",
  "phone": "(555) 123-4567",
  "email": "john@example.com",
  "address": "123 Main St, Anytown, USA"
}
```

## Phone Number Formatting

The application automatically formats phone numbers:
- **10-digit**: `5551234567` → `(555) 123-4567`
- **With country code**: `15551234567` → `+1 (555) 123-4567`
- **Existing format**: `(555) 123-4567` → `(555) 123-4567`

## Menu Options

1. **Add new contact**: Create a new contact with name, phone, email, and address
2. **List all contacts**: View all contacts in a formatted list
3. **Search contacts**: Find contacts by searching any field
4. **Edit contact**: Modify existing contact information
5. **Delete contact**: Remove contacts from the address book
6. **Show statistics**: View address book statistics
7. **Export to CSV**: Export all contacts to a CSV file
8. **Exit**: Save and quit the application

## CSV Export

Export contacts to CSV format with proper escaping:
- Filename can be customized (default: `contacts.csv`)
- Fields: Name, Phone, Email, Address
- Proper CSV escaping for commas and quotes

## Testing

Run the unit tests:
```bash
python -m pytest test_address_book.py -v
```

Or run with unittest:
```bash
python test_address_book.py
```

## Keyboard Controls

- **Ctrl+C**: Exit the application at any time
- **Ctrl+D**: Exit the application at any time

## Examples

### Contact Management Workflow
```bash
# Add contacts
1. Add new contact -> "John Doe" -> "555-123-4567" -> "john@example.com"
1. Add new contact -> "Jane Smith" -> "555-987-6543" -> "jane@example.com"

# Search for contacts
3. Search contacts -> "john" -> Finds John Doe

# Edit contact
4. Edit contact -> Select John Doe -> Update phone number

# Export contacts
7. Export to CSV -> "my_contacts.csv"

# View statistics
6. Show statistics -> Shows total contacts, data completeness
```

### Search Examples
```bash
# Search by name
3. Search contacts -> "john" -> Finds contacts with "john" in name

# Search by phone
3. Search contacts -> "555-123" -> Finds contacts with that phone pattern

# Search by email domain
3. Search contacts -> "example.com" -> Finds all contacts with that domain
```

## File Operations

- **Auto-save**: Contacts are saved automatically after any change
- **Auto-load**: Contacts are loaded when the application starts
- **Backup**: You can manually backup `contacts.json` file
- **Reset**: Delete `contacts.json` to start with a clean address book
- **CSV Export**: Create spreadsheet-compatible exports

## Error Handling

The application handles various error conditions:
- Invalid menu choices
- Empty contact names
- Invalid phone/email formats (with warnings)
- File I/O errors (with fallback to empty list)
- Keyboard interrupts (graceful exit)
- CSV export errors

## Data Privacy

- All data is stored locally in JSON format
- No external API calls or data transmission
- CSV exports are created locally
- You maintain full control over your contact data

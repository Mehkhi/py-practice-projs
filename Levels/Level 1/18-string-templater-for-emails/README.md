# String Templater for Emails

A Python command-line program that creates personalized emails from templates by replacing variables with provided data. Perfect for generating bulk emails, notifications, and automated communications.

## Features

### Core Features
- **Template Loading**: Load email templates from files or enter them manually
- **Variable Detection**: Automatically detect variables in `{{variable_name}}` format
- **Variable Replacement**: Replace template variables with provided data
- **Email Generation**: Output personalized emails with filled variables

### Advanced Features
- **JSON Data Support**: Load recipient data from JSON files
- **Conditional Sections**: Use `{{if variable}}...{{else}}...{{endif}}` for conditional content
- **Batch Processing**: Generate multiple emails at once
- **Interactive Mode**: User-friendly command-line interface

## Installation

No additional dependencies required! This program uses only Python standard library modules.

## Usage

### Basic Usage

Run the program interactively:

```bash
python string_templater_for_emails.py
```

The program will guide you through:
1. Loading or entering your email template
2. Choosing how to provide data (manual, JSON file, or batch mode)
3. Generating the personalized emails

### Template Format

Use `{{variable_name}}` syntax for variables in your templates:

```
Hello {{name}},

Thank you for your order {{order_id}}.
{{if premium}}
As a premium member, you get free shipping!
{{else}}
Shipping costs $5.99.
{{endif}}

Best regards,
{{company_name}}
```

### Data Formats

#### Manual Entry
Enter values for each variable when prompted.

#### JSON File Format
```json
{
  "name": "John Doe",
  "order_id": "ORD-12345",
  "premium": true,
  "company_name": "Widget Store"
}
```

#### Batch JSON Format
```json
[
  {
    "name": "John Doe",
    "order_id": "ORD-12345",
    "premium": true
  },
  {
    "name": "Jane Smith",
    "order_id": "ORD-67890",
    "premium": false
  }
]
```

## Examples

### Example 1: Simple Welcome Email

**Template:**
```
Welcome {{name}}!

Thank you for joining {{company}}. Your account is now active.

Best regards,
The {{company}} Team
```

**Data:**
```json
{
  "name": "Alice Johnson",
  "company": "TechCorp"
}
```

**Output:**
```
Welcome Alice Johnson!

Thank you for joining TechCorp. Your account is now active.

Best regards,
The TechCorp Team
```

### Example 2: Order Confirmation with Conditional Content

**Template:**
```
Dear {{customer_name}},

Your order {{order_id}} has been confirmed.

{{if premium}}
As a premium member, you get:
- Free shipping
- Priority processing
- 10% discount on future orders
{{else}}
Standard shipping applies. Consider upgrading to premium for benefits!
{{endif}}

Order total: ${{total}}

Thank you for your business!
{{company_name}}
```

**Data:**
```json
{
  "customer_name": "Bob Wilson",
  "order_id": "ORD-2024-001",
  "premium": true,
  "total": "49.99",
  "company_name": "Gadget Store"
}
```

**Output:**
```
Dear Bob Wilson,

Your order ORD-2024-001 has been confirmed.

As a premium member, you get:
- Free shipping
- Priority processing
- 10% discount on future orders

Order total: $49.99

Thank you for your business!
Gadget Store
```

### Example 3: Batch Email Generation

**Template:**
```
Hi {{name}},

Your subscription to {{service}} expires on {{expiry_date}}.

{{if auto_renew}}
Your subscription will auto-renew. No action needed.
{{else}}
Please renew your subscription to continue using {{service}}.
{{endif}}

Thanks,
{{company}} Support
```

**Batch Data:**
```json
[
  {
    "name": "Alice",
    "service": "Premium Plan",
    "expiry_date": "2024-12-31",
    "auto_renew": true,
    "company": "TechCorp"
  },
  {
    "name": "Bob",
    "service": "Basic Plan",
    "expiry_date": "2024-12-15",
    "auto_renew": false,
    "company": "TechCorp"
  }
]
```

## Running Tests

Run the unit tests to verify functionality:

```bash
python test_string_templater_for_emails.py
```

Or with verbose output:

```bash
python -m unittest test_string_templater_for_emails -v
```

## File Structure

```
18-string-templater-for-emails/
├── string_templater_for_emails.py    # Main program
├── test_string_templater_for_emails.py  # Unit tests
├── README.md                         # This file
├── CHECKLIST.md                      # Feature checklist
└── SPEC.md                          # Project specification
```

## Error Handling

The program handles various error conditions gracefully:

- **Invalid template files**: Shows error message and continues
- **Missing variables**: Leaves `{{variable}}` placeholders unchanged
- **Invalid JSON**: Shows error message and continues
- **Empty input**: Prompts user to provide required information

## Tips for Best Results

1. **Use descriptive variable names**: `{{customer_name}}` is better than `{{name}}`
2. **Test with sample data**: Always test your templates with sample data first
3. **Use conditional sections**: Make emails more personalized with conditional content
4. **Validate your JSON**: Ensure JSON files are properly formatted
5. **Backup your templates**: Keep copies of your email templates

## Troubleshooting

### Common Issues

**Q: Variables aren't being replaced**
A: Check that variable names match exactly (case-sensitive) and use `{{variable_name}}` format.

**Q: Conditional sections not working**
A: Ensure you use the exact format: `{{if variable}}...{{else}}...{{endif}}`

**Q: JSON file not loading**
A: Verify the JSON file exists and is properly formatted. Use a JSON validator.

**Q: Program crashes on invalid input**
A: The program is designed to handle errors gracefully. If it crashes, please report the issue.

## Contributing

This is a learning project, but suggestions for improvements are welcome:

- Additional template features
- Better error messages
- More output formats
- GUI interface
- Email sending integration

## License

This project is part of a Python learning curriculum and is available for educational use.

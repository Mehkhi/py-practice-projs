# Email Sender

A professional command-line email sender with support for attachments, HTML templates, batch processing, and comprehensive error handling.

## Features

### Core Features
- ✅ **SMTP Email Sending**: Send emails via any SMTP server with TLS support
- ✅ **Attachments**: Attach multiple files to your emails
- ✅ **HTML Templates**: Send rich HTML emails with CSS styling
- ✅ **CSV Recipients**: Load recipient lists from CSV files
- ✅ **Error Handling**: Comprehensive error handling for all operations

### Bonus Features
- ✅ **Email Validation**: Validate email addresses before sending
- ✅ **Batch Processing**: Send emails in batches with rate limiting
- ✅ **Delivery Tracking**: Track successful and failed email deliveries
- ✅ **Logging**: Detailed logging for debugging and monitoring

## Installation

### Prerequisites
- Python 3.8 or higher
- pip for package management

### Setup

1. **Clone or download the project**
   ```bash
   cd 13-email-sender
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Basic Commands

#### Send a Single Email
```bash
python -m email_sender send \
  --smtp smtp.gmail.com \
  --port 587 \
  --user your@email.com \
  --pass yourpassword \
  --to recipient@example.com \
  --subject "Test Email" \
  --body "Hello, this is a test email!"
```

#### Send with HTML Template and Attachments
```bash
python -m email_sender send \
  --smtp smtp.gmail.com \
  --port 587 \
  --user your@email.com \
  --pass yourpassword \
  --to recipient@example.com \
  --subject "Newsletter" \
  --body "Check out our latest newsletter!" \
  --html newsletter.html \
  --attach report.pdf image.jpg
```

#### Send Batch Emails from CSV
```bash
python -m email_sender batch \
  --smtp smtp.gmail.com \
  --port 587 \
  --user your@email.com \
  --pass yourpassword \
  --recipients recipients.csv \
  --subject "Monthly Update" \
  --body "Here's your monthly update" \
  --batch-size 5 \
  --delay 2.0
```

#### Create Sample Files
```bash
python -m email_sender samples
```

### Command Line Options

#### Send Command
- `--smtp`: SMTP server hostname (required)
- `--port`: SMTP server port (required)
- `--user`: SMTP username/email (required)
- `--pass`: SMTP password (required)
- `--to`: Recipient email addresses (required, multiple allowed)
- `--subject`: Email subject (required)
- `--body`: Email body text (required)
- `--html`: HTML template file (optional)
- `--attach`: Attachment file paths (optional, multiple allowed)
- `--no-tls`: Disable TLS encryption (optional)

#### Batch Command
- All send command options plus:
- `--recipients`: CSV file with recipients (required)
- `--batch-size`: Emails per batch (default: 10)
- `--delay`: Delay between batches in seconds (default: 1.0)

#### Global Options
- `-v, --verbose`: Enable verbose logging
- `--version`: Show version information

## Configuration

### SMTP Server Settings

#### Gmail
```
SMTP Server: smtp.gmail.com
Port: 587 (TLS) or 465 (SSL)
Authentication: Your Gmail address and App Password
```

#### Outlook/Hotmail
```
SMTP Server: smtp-mail.outlook.com
Port: 587 (TLS)
Authentication: Your Outlook email and password
```

#### Custom SMTP
```
SMTP Server: your-smtp-server.com
Port: 587 (TLS) or 25 (no encryption)
Authentication: Your credentials
```

### CSV Recipients Format

Create a CSV file with recipient data:

```csv
email,name,company
john@example.com,John Doe,Acme Corp
jane@example.com,Jane Smith,Tech Inc
bob@example.com,Bob Wilson,Startup LLC
```

Required columns:
- `email`: Recipient email address (required)

Optional columns:
- `name`: Recipient name
- `company`: Company name
- Any other data for template substitution

### HTML Template Format

Create HTML templates with placeholders:

```html
<!DOCTYPE html>
<html>
<head>
    <title>Newsletter</title>
    <style>
        body { font-family: Arial, sans-serif; }
        .header { background-color: #f0f0f0; padding: 20px; }
        .content { padding: 20px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Hello {name}!</h1>
    </div>
    <div class="content">
        <p>Welcome to our newsletter, {name} from {company}!</p>
        <p>This is a sample HTML email template.</p>
    </div>
</body>
</html>
```

## Examples

### Example 1: Simple Newsletter
```bash
# Create sample files
python -m email_sender samples

# Send newsletter to all recipients
python -m email_sender batch \
  --smtp smtp.gmail.com \
  --port 587 \
  --user your@email.com \
  --pass yourpassword \
  --recipients sample_recipients.csv \
  --subject "Monthly Newsletter" \
  --body "Check out our latest updates!" \
  --html sample_template.html
```

### Example 2: Invoice with Attachment
```bash
python -m email_sender send \
  --smtp smtp.gmail.com \
  --port 587 \
  --user billing@company.com \
  --pass yourpassword \
  --to customer@example.com \
  --subject "Invoice #12345" \
  --body "Please find your invoice attached." \
  --attach invoice_12345.pdf
```

### Example 3: Marketing Campaign
```bash
python -m email_sender batch \
  --smtp smtp.gmail.com \
  --port 587 \
  --user marketing@company.com \
  --pass yourpassword \
  --recipients customers.csv \
  --subject "Special Offer - 50% Off!" \
  --body "Don't miss our special offer!" \
  --html promotion.html \
  --attach coupon.pdf \
  --batch-size 20 \
  --delay 1.5
```

## Testing

Run the test suite:

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=email_sender

# Run with verbose output
pytest tests/ -v
```

## Logging

The application provides detailed logging for debugging and monitoring:

```bash
# Enable verbose logging
python -m email_sender send --verbose [other options]
```

Log levels:
- `INFO`: General operation information
- `WARNING`: Non-critical issues
- `ERROR`: Error conditions
- `DEBUG`: Detailed debugging information (verbose mode only)

## Error Handling

The application handles various error conditions:

- **SMTP Connection Errors**: Invalid server, port, or network issues
- **Authentication Errors**: Invalid credentials
- **Email Validation**: Invalid email addresses
- **File Errors**: Missing attachments or CSV files
- **Template Errors**: Invalid HTML templates
- **Rate Limiting**: SMTP server rate limits

## Security Considerations

- Use App Passwords for Gmail (not your regular password)
- Store credentials securely (consider environment variables)
- Use TLS encryption for SMTP connections
- Validate all email addresses before sending
- Be mindful of rate limits to avoid being blocked

## Troubleshooting

### Common Issues

1. **Authentication Failed**
   - Check your email and password
   - For Gmail, use an App Password
   - Ensure 2FA is enabled if required

2. **Connection Refused**
   - Verify SMTP server and port
   - Check firewall settings
   - Try different ports (587, 465, 25)

3. **Recipients Refused**
   - Validate email addresses
   - Check for typos in recipient list
   - Verify recipient domains exist

4. **Attachments Too Large**
   - Check file sizes (default limit: 25MB)
   - Compress large files
   - Use cloud storage links instead

### Debug Mode

Enable verbose logging to see detailed information:

```bash
python -m email_sender send --verbose [options]
```

## Limitations

- Maximum attachment size: 25MB per file
- Batch size limited by SMTP server rate limits
- HTML templates use simple string substitution
- No support for inline images (use attachments)
- No email scheduling (send immediately)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## License

This project is part of the Python Practice Projects series and is available for educational purposes.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review the logs with verbose mode
3. Check SMTP server documentation
4. Verify your credentials and settings

---

**Note**: This tool is for legitimate email sending purposes only. Always comply with anti-spam laws and email service provider terms of service.

# Mail Merge - Personal Email Campaign Manager

A professional mail merge application similar to GMass, with support for Gmail API, Google Sheets sync, campaign tracking, and both CLI and web UI interfaces.

## Features

### Core Features
- ✅ **Gmail API Integration**: Send emails via Gmail API with OAuth2 authentication
- ✅ **Campaign Management**: Create and track multiple email campaigns
- ✅ **CSV Import**: Import recipients from local CSV files
- ✅ **Google Sheets Sync**: Sync recipient data from Google Sheets
- ✅ **Template Personalization**: Personalize emails with recipient data (e.g., {name}, {company})
- ✅ **Status Tracking**: Track sent/failed/queued status for each recipient
- ✅ **Web UI**: Lightweight web interface for managing campaigns
- ✅ **CLI Interface**: Full-featured command-line interface

### Additional Features
- ✅ **SMTP Fallback**: Support for SMTP sending as alternative to Gmail API
- ✅ **HTML Templates**: Send rich HTML emails with CSS styling
- ✅ **Attachments**: Attach multiple files to your emails
- ✅ **Email Validation**: Validate email addresses before sending
- ✅ **Batch Processing**: Send emails in batches with rate limiting
- ✅ **Export Results**: Export campaign results to CSV
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

4. **Set up Gmail API credentials (for Gmail sending)**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select an existing one
   - Enable Gmail API and Google Sheets API
   - Create OAuth 2.0 credentials (Desktop app)
   - Download credentials and save as `credentials.json` in the project root
   - On first run, the app will open a browser for OAuth authentication
   - Token will be saved to `token.json` for future use

## Usage

### Mail Merge Campaigns (New)

#### Create a Campaign
```bash
python -m email_sender campaign create \
  --name "Monthly Newsletter" \
  --subject "Hello {name}, check out our updates!" \
  --body "Hi {name}, this is your monthly update from {company}." \
  --html template.html \
  --source-type csv
```

#### Import Recipients from CSV
```bash
python -m email_sender campaign import-csv \
  --campaign-id 1 \
  --csv recipients.csv
```

#### Sync Recipients from Google Sheet
```bash
python -m email_sender campaign sync-sheet \
  --campaign-id 1 \
  --sheet-id "https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID" \
  --range "Sheet1!A1:Z1000"
```

#### Send Campaign Emails
```bash
python -m email_sender campaign send \
  --campaign-id 1 \
  --transport gmail \
  --batch-size 10 \
  --delay 1.0
```

#### List All Campaigns
```bash
python -m email_sender campaign list
```

#### View Campaign Status
```bash
python -m email_sender campaign status --campaign-id 1
```

#### Export Campaign Results
```bash
python -m email_sender campaign export \
  --campaign-id 1 \
  --output results.csv
```

#### Start Web UI
```bash
python -m email_sender web
```
Then open http://127.0.0.1:9002 in your browser.

**Note:** The default port is 9002 to avoid conflicts with common services (macOS AirPlay uses 5000, many dev servers use 8000/8080).

### Legacy Commands (Still Supported)

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

### Database

Campaign data is stored in a SQLite database (`mail_merge.db`) in the project directory. This database tracks:
- Campaigns (name, subject, templates, source info)
- Recipients (email, personalization data, status)
- Send status (queued, sent, failed with error messages)
- Timestamps for all operations

The database is automatically created on first use. You can delete `mail_merge.db` to start fresh.

### Gmail API Setup

1. **Create Google Cloud Project**
   - Visit [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select existing

2. **Enable APIs**
   - Enable "Gmail API"
   - Enable "Google Sheets API"

3. **Create OAuth 2.0 Credentials**
   - Go to "Credentials" → "Create Credentials" → "OAuth client ID"
   - Choose "Desktop app" as application type
   - Download the JSON file and save as `credentials.json` in project root

4. **First Run Authentication**
   - When you first use Gmail API or Sheets sync, a browser window will open
   - Sign in with your Google account and authorize the app
   - Token will be saved to `token.json` for future use

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
- Any other data for template substitution (accessible via {column_name} in templates)

### Google Sheets Format

Your Google Sheet should have:
- First row: Column headers (must include `email`)
- Subsequent rows: Recipient data
- Same column structure as CSV (email required, other columns for personalization)

Share the sheet with the service account email or make it publicly readable (read-only).

### HTML Template Format

Create HTML templates with placeholders that will be replaced with recipient data:

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

**Template Variables:**
- Use `{column_name}` syntax to insert recipient data
- All CSV/Sheet columns are available as variables
- Missing variables are left as-is (not replaced)
- Example: `{name}`, `{company}`, `{email}`, etc.

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

### Credentials and Tokens
- **Never commit** `credentials.json` or `token.json` to version control
- These files are automatically added to `.gitignore`
- Store OAuth credentials securely and restrict access
- Use App Passwords for Gmail SMTP (not your regular password)
- Consider using environment variables for sensitive data

### Database
- The SQLite database (`mail_merge.db`) contains recipient email addresses
- Keep the database file secure and backed up
- Consider encrypting the database for production use

### Best Practices
- Use TLS encryption for SMTP connections
- Validate all email addresses before sending
- Be mindful of rate limits to avoid being blocked
- Only send to recipients who have opted in
- Comply with anti-spam laws (CAN-SPAM, GDPR, etc.)
- Use the web UI only on trusted networks (defaults to localhost)

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

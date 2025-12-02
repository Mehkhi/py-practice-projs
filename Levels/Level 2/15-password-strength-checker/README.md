# Password Strength Checker

A comprehensive command-line tool for evaluating password security, providing detailed feedback and improvement suggestions.

## Features

- **Length Analysis**: Evaluates password length for optimal security
- **Character Diversity**: Checks for uppercase, lowercase, digits, and special characters
- **Common Password Detection**: Identifies commonly used weak passwords
- **Pattern Detection**: Detects sequential and repeated character patterns
- **Entropy Calculation**: Measures password randomness in bits
- **Have I Been Pwned Integration**: Checks against known data breaches
- **Smart Feedback**: Provides actionable improvement suggestions
- **Password Generation**: Creates strong password suggestions

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Setup

1. Clone or download this repository
2. Navigate to the project directory:
   ```bash
   cd 15-password-strength-checker
   ```

3. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Basic Password Check

```bash
# Check a password
python -m password_strength_checker "mypassword123"

# Check interactively (password hidden)
python -m password_strength_checker
```

### Generate Strong Password

```bash
# Generate a 12-character password (default)
python -m password_strength_checker --generate

# Generate a longer password
python -m password_strength_checker --generate --length 16
```

### Detailed Analysis

```bash
# Show detailed scoring breakdown
python -m password_strength_checker --details "MyPassword123!"

# Skip Have I Been Pwned check (faster, no network required)
python -m password_strength_checker --no-hibp-check "password"
```

### Command Line Options

```
usage: python -m password_strength_checker [-h] [-g] [-l LENGTH] [-d] [--no-hibp-check] [-v] [password]

Check password strength and get improvement suggestions

positional arguments:
  password              Password to evaluate (if not provided, will prompt securely)

optional arguments:
  -h, --help            Show this help message and exit
  -g, --generate        Generate a strong password suggestion
  -l LENGTH, --length LENGTH
                        Length for generated password (default: 12, minimum: 8)
  -d, --details         Show detailed scoring breakdown
  --no-hibp-check       Skip Have I Been Pwned API check
  -v, --verbose         Enable verbose logging
```

## Examples

### Example 1: Weak Password
```bash
$ python -m password_strength_checker "password"

Password Strength: Weak (15/100)

Feedback:
  • This is a commonly used password. Choose something unique.
  • Add uppercase letters (A-Z).
  • Add numbers (0-9).
  • Add special characters (!@#$%^&*).
  • Use at least 3 different character types.
  • Password is weak. Consider improvements above.
```

### Example 2: Strong Password with Details
```bash
$ python -m password_strength_checker --details "MySecurePass123!"

Password Strength: Strong (75/100)

Detailed Scores:
  Length: 20/25
  Diversity: 25/25
  Pattern Penalty: -0
  Entropy: 96.34 bits

✅ Not found in known data breaches.

Feedback:
  • Great password strength!
```

### Example 3: Password Generation
```bash
$ python -m password_strength_checker --generate --length 14

Generated strong password (14 characters):
  Tr8$jK9#mP2&vL

Keep this password safe and don't share it!
```

### Example 4: Breached Password Detection
```bash
$ python -m password_strength_checker "123456"

Password Strength: Very Weak (0/100)

🚨 CRITICAL: Found in 1424333 data breaches!

Feedback:
  • Password is too short. Use at least 8 characters.
  • Add lowercase letters (a-z).
  • Add uppercase letters (A-Z).
  • Add special characters (!@#$%^&*).
  • This is a commonly used password. Choose something unique.
  • Password is very weak. Major improvements needed.
```

## Scoring System

Passwords are evaluated on a 0-100 scale:

- **0-19**: Very Weak - Major security risk
- **20-39**: Weak - Vulnerable to basic attacks
- **40-59**: Moderate - Better than most, but could be stronger
- **60-79**: Strong - Good protection against most threats
- **80-100**: Very Strong - Excellent security

### Scoring Components

- **Length (0-25 points)**: Rewards longer passwords
- **Diversity (0-25 points)**: Awards different character types
- **Penalties**: Deducted for common passwords and weak patterns

## Security Features

### Have I Been Pwned Integration

The tool checks passwords against the Have I Been Pwned database using k-anonymity:

1. Creates SHA-1 hash of your password
2. Sends only the first 5 characters to the API
3. Searches locally for matches in the response
4. Never transmits your actual password

### Privacy Protection

- Passwords are never stored or logged
- Network requests are made securely over HTTPS
- No personal data is collected or transmitted

## Development

### Running Tests

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest --cov=password_strength_checker tests/

# Run specific test
pytest tests/test_password_strength_checker.py::TestLengthScoring::test_short_password
```

### Code Quality

The codebase follows these standards:

- **Linting**: `ruff check .`
- **Formatting**: `black .`
- **Type checking**: `mypy password_strength_checker/`

### Project Structure

```
15-password-strength-checker/
├── password_strength_checker/
│   ├── __init__.py          # Package initialization
│   ├── main.py              # CLI entry point
│   ├── core.py              # Core password evaluation logic
│   └── utils.py             # Utility functions
├── tests/
│   ├── __init__.py
│   └── test_password_strength_checker.py
├── requirements.txt         # Python dependencies
├── README.md                # This file
├── CHECKLIST.md             # Feature checklist
└── SPEC.md                  # Project specifications
```

## API Reference

### Core Functions

#### `evaluate_password(password, check_hibp=True)`

Evaluates a password and returns detailed results.

**Parameters:**
- `password` (str): Password to evaluate
- `check_hibp` (bool): Whether to check Have I Been Pwned API

**Returns:** Dictionary with:
- `score` (int): Overall strength score (0-100)
- `strength` (str): Strength category
- `length_score` (int): Length component score
- `diversity_score` (int): Diversity component score
- `pattern_penalty` (int): Pattern penalty applied
- `entropy` (float): Password entropy in bits
- `is_common` (bool): Whether password is common
- `hibp_count` (int/None): Breach count from HIBP
- `feedback` (list): List of improvement suggestions

#### `generate_password_suggestion(length=12)`

Generates a strong random password.

**Parameters:**
- `length` (int): Desired password length (minimum 8)

**Returns:** Generated password string

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Format code with Black and Ruff
6. Submit a pull request

## License

This project is open source. See individual files for license information.

## Security Notice

This tool is designed to help improve password security. However:

- Never use this tool with real passwords you currently use
- Generated passwords should be stored securely
- Always use unique passwords for different accounts
- Consider using a password manager for secure storage

## Troubleshooting

### Network Issues

If you encounter network errors with the Have I Been Pwned check:
- Use `--no-hibp-check` to skip the online check
- Check your internet connection
- The API may be temporarily unavailable

### Installation Issues

If pip install fails:
- Ensure you have Python 3.8+
- Try updating pip: `pip install --upgrade pip`
- Use a virtual environment to avoid conflicts

### Performance Issues

For slow performance:
- Use `--no-hibp-check` to skip network requests
- The tool is optimized for typical password lengths
- Very long passwords (>100 chars) may take slightly longer

## Changelog

### Version 1.0.0
- Initial release
- Core password strength evaluation
- Have I Been Pwned integration
- Password generation
- Comprehensive test suite
- CLI interface with multiple options

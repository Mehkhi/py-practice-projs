# Password Generator

A command-line program that generates secure, random passwords with customizable length, character classes, and advanced security features. Perfect for creating strong passwords for online accounts, applications, and security-conscious users.

## Features

### Core Features
- **Customizable Length**: Generate passwords from 4 to 128 characters
- **Character Class Selection**: Choose from uppercase, lowercase, digits, and symbols
- **Class Enforcement**: Ensure at least one character from each selected class
- **Random Generation**: Cryptographically secure random password generation

### Advanced Features
- **Password Strength Analysis**: Calculate entropy and assess password strength
- **Passphrase Generation**: Create memorable passphrases from word lists
- **Clipboard Integration**: Copy generated passwords to system clipboard
- **Color-Coded Output**: Visual strength indicators with color coding
- **Interactive Configuration**: Easy-to-use menu system

## Installation

No installation required! This program uses only Python's standard library.

### Requirements
- Python 3.7 or higher
- Optional: System clipboard support (automatically detected)

## Usage

### Running the Program
```bash
python password_generator.py
```

### Interactive Menu
Once running, you'll see a menu with these options:

1. **Generate password** - Create a secure random password
2. **Generate passphrase** - Create a memorable word-based passphrase
3. **Configure character classes** - Toggle character types on/off
4. **Password strength analyzer** - Analyze any password's strength
5. **Copy to clipboard** - Copy text to system clipboard
6. **Exit** - Quit the program

### Example Session
```
$ python password_generator.py
Welcome to the Password Generator!
Generate secure passwords and passphrases with ease.

============================================================
[LOCK] PASSWORD GENERATOR [LOCK]
============================================================
1. Generate password
2. Generate passphrase
3. Configure character classes
4. Password strength analyzer
5. Copy to clipboard
6. Exit
============================================================

Enter your choice (1-6): 1

========================================
[KEY] PASSWORD GENERATION
========================================
Enter password length (4-128): 16
Ensure at least one character from each class? (y/n): y

[KEY] Generated Password:
   7Kp$mN2@xR9#sT4w

[BAR CHART] Password Analysis:
   Length: 16 characters
   Entropy: 95.52 bits
   Strength: Strong
   Contains:
     Uppercase: [OK]
     Lowercase: [OK]
     Digits: [OK]
     Symbols: [OK]

Press Enter to continue...
```

## Password Generation Options

### Character Classes
- **Uppercase Letters**: A-Z (26 characters)
- **Lowercase Letters**: a-z (26 characters)
- **Digits**: 0-9 (10 characters)
- **Symbols**: !@#$%^&*()_+-=[]{}|;:,.<>? (26 characters)

### Password Length
- **Minimum**: 4 characters
- **Maximum**: 128 characters
- **Recommended**: 12+ characters for good security

### Class Enforcement
When enabled, ensures that generated passwords contain at least one character from each selected character class. This guarantees complexity and meets most password requirements.

## Passphrase Generation

Create memorable passphrases using:
- **Word Count**: 2-10 words from a curated word list
- **Custom Separators**: Choose any separator (default: -)
- **Capitalization**: Option to capitalize first letter of each word
- **Number Inclusion**: Option to add random number at the end

### Example Passphrases
- `Sunset-Dragon-Quantum-42`
- `CoffeeMountainOcean789`
- `Rainbow_Phoenix_Galaxy_123`

## Password Strength Analysis

### Entropy Calculation
Password strength is measured in bits of entropy:
- **Very Weak**: < 40 bits
- **Weak**: 40-60 bits
- **Moderate**: 60-80 bits
- **Strong**: 80-100 bits
- **Very Strong**: > 100 bits

### Strength Factors
- **Length**: Longer passwords are generally stronger
- **Character Diversity**: More character types increase complexity
- **Randomness**: Truly random generation prevents patterns

### Analysis Features
- Real-time entropy calculation
- Character type analysis
- Visual strength indicators with color coding
- Personalized security recommendations

## Security Features

### Cryptographic Security
- Uses Python's `random` module for secure random generation
- No predictable patterns or sequences
- Proper character distribution

### Best Practices
- Enforces minimum length requirements
- Encourages character diversity
- Provides security education
- No password storage or logging

## Testing

Run the unit tests to verify functionality:

```bash
python -m pytest test_password_generator.py -v
```

Or run with unittest:

```bash
python -m unittest test_password_generator.py
```

### Test Coverage
- Password generation with various options
- Passphrase generation and customization
- Entropy calculation and strength assessment
- Input validation and error handling
- Character class configuration
- Integration workflows

## Project Structure

```
15-password-generator/
├── password_generator.py       # Main program
├── test_password_generator.py  # Unit tests
├── README.md                   # This file
├── CHECKLIST.md                # Feature checklist
└── SPEC.md                     # Project specification
```

## Code Structure

### Main Classes

#### `PasswordGenerator`
The core class that handles all password generation functionality:

- `validate_length()` - Validate password length input
- `get_enabled_character_classes()` - Get active character sets
- `generate_password()` - Create secure random passwords
- `generate_passphrase()` - Create memorable passphrases
- `calculate_entropy()` - Calculate password entropy
- `assess_password_strength()` - Analyze password security
- `copy_to_clipboard()` - System clipboard integration

### Key Functions

- `display_menu()` - Show interactive menu options
- `handle_*()` methods - Process user choices
- `main()` - Main application loop

## Use Cases

### Personal Security
- **Online Accounts**: Generate unique passwords for each service
- **Application Security**: Create strong passwords for software
- **Device Security**: Secure passwords for phones, computers, etc.

### Professional Use
- **IT Administration**: Generate passwords for user accounts
- **Development**: Create secure credentials for applications
- **Compliance**: Meet organizational password requirements

### Education
- **Security Training**: Teach password best practices
- **Security Awareness**: Demonstrate password strength concepts
- **Cryptographic Learning**: Understand entropy and randomness

## Clipboard Integration

The password generator supports copying to clipboard on:
- **macOS**: Uses `pbcopy` command
- **Windows**: Uses `clip` command
- **Linux**: Uses `xclip` or `xsel` commands

If clipboard integration is not available, you can manually copy the generated password.

## Security Considerations

### What This Tool Does Well
- Generates truly random passwords
- Calculates accurate entropy measurements
- Provides educational security feedback
- No password storage or transmission

### Limitations
- Relies on system's random number generator
- Clipboard integration may not work on all systems
- Generated passwords should still be stored securely

### Best Practices
- Use unique passwords for each account
- Combine with a password manager for storage
- Enable two-factor authentication when available
- Regularly update important passwords

## Performance

- Fast password generation (milliseconds)
- Minimal memory usage
- Efficient entropy calculations
- Responsive user interface

## Troubleshooting

### Common Issues

**"No character classes enabled" error**
- Go to option 3 (Configure character classes)
- Enable at least one character class
- Try generating password again

**Clipboard not working**
- Check if your system supports clipboard commands
- Install required tools (xclip/xsel on Linux)
- Manually copy the password as fallback

**Password seems weak**
- Increase password length
- Enable more character classes
- Check the entropy calculation

**Generated password doesn't meet requirements**
- Enable class enforcement option
- Configure appropriate character classes
- Adjust length to meet requirements

### Performance Tips

- Longer passwords take slightly longer to generate
- Passphrases are generally faster to generate
- Entropy calculation is very fast
- Clipboard operations depend on system performance

## Learning Objectives

This project demonstrates:
- **Random number generation** for security
- **String manipulation** and character handling
- **Mathematical calculations** (entropy, logarithms)
- **Input validation** with detailed error messages
- **System integration** (clipboard, subprocess)
- **Security concepts** (entropy, strength assessment)
- **User interface design** for CLI applications
- **Cross-platform compatibility**

## Extension Ideas

After mastering the basics, consider adding:
- GUI interface with tkinter or PyQt
- Password policy compliance checking
- Batch password generation
- Password history tracking
- Integration with password managers
- Advanced entropy analysis
- Custom word lists for passphrases
- Pronounceable password generation

## Contributing

This is a learning project. Feel free to:
- Add new character classes
- Improve strength algorithms
- Enhance user interface
- Add more test cases
- Optimize performance
- Add new export formats

## License

This project is open source and available for educational purposes.

---

**[LOCK] Stay Secure! [LOCK]**

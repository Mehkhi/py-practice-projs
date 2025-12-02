# Palindrome & Anagram Checker

A command-line tool that checks if strings are palindromes or if two strings are anagrams of each other.

## What It Does

This program provides three main functions:
1. **Palindrome Checker**: Determines if a string reads the same forwards and backwards
2. **Anagram Checker**: Determines if two strings contain the same characters in different orders
3. **Batch File Processing**: Checks multiple lines in a file for palindromes

The program normalizes strings by removing spaces, punctuation, and converting to lowercase before checking.

## How to Run

1. Make sure you have Python 3.7 or higher installed
2. Run the program:
   ```bash
   python palindrome_anagram_checker.py
   ```
3. Follow the menu prompts to choose what you want to check

## Example Usage

### Palindrome Checking
```
=== Palindrome Checker ===
Enter text to check if it's a palindrome: A man, a plan, a canal: Panama
[OK] 'A man, a plan, a canal: Panama' is a palindrome!
```

### Anagram Checking
```
=== Anagram Checker ===
Enter first string: Dormitory
Enter second string: Dirty room
[OK] 'Dormitory' and 'Dirty room' are anagrams!
```

### Batch File Processing
```
=== Batch File Checker ===
Enter filename to process: sample.txt

Processing 3 lines from sample.txt:
--------------------------------------------------
Line 1: 'racecar' → PALINDROME
Line 2: 'hello' → Not a palindrome
Line 3: 'level' → PALINDROME
```

## Features

- **String Normalization**: Automatically removes spaces, punctuation, and converts to lowercase
- **Palindrome Detection**: Efficient algorithm using string reversal
- **Anagram Detection**: Character counting using collections.Counter
- **Interactive Menu**: User-friendly command-line interface
- **Batch Processing**: Process multiple lines from a file
- **Error Handling**: Graceful handling of invalid input and file errors
- **Unicode Support**: Basic support for Unicode characters

## Testing

Run the unit tests:
```bash
python -m pytest test_palindrome_anagram_checker.py -v
```

Or run with unittest:
```bash
python test_palindrome_anagram_checker.py
```

## Algorithm Details

### Palindrome Detection
1. Normalize the string (remove non-alphanumeric characters, lowercase)
2. Compare the normalized string with its reverse
3. Return True if they match, False otherwise

### Anagram Detection
1. Normalize both strings
2. Check if lengths are equal (quick optimization)
3. Count character frequencies using collections.Counter
4. Compare the character count dictionaries
5. Return True if they match, False otherwise

## Examples

### Palindromes
- "racecar" → True
- "A man, a plan, a canal: Panama" → True
- "Was it a car or a cat I saw?" → True
- "hello" → False

### Anagrams
- "listen" and "silent" → True
- "Dormitory" and "Dirty room" → True
- "The eyes" and "They see" → True
- "hello" and "world" → False

# Word Count Tool

A comprehensive text analysis tool that counts words, lines, characters, and provides detailed statistics about text files.

## What It Does

This program provides complete text analysis functionality:
- Count words, lines, characters, and paragraphs
- Calculate reading time and average word length
- Find most common words and word frequencies
- Exclude common stop words from analysis
- Compare multiple files
- Handle both file input and direct text input

## How to Run

1. Make sure you have Python 3.7 or higher installed
2. Run the program:
   ```bash
   python word_count.py
   ```
3. Or analyze a file directly:
   ```bash
   python word_count.py filename.txt
   ```
4. Follow the menu prompts to analyze text

## Example Usage

### Command Line Analysis
```bash
$ python word_count.py sample.txt

==================================================
[BAR CHART] TEXT STATISTICS
==================================================
File: sample.txt
Characters:       1,234
Characters (no spaces): 1,045
Words:            198
Lines:            25
Paragraphs:       5
Unique words:     142
Avg word length:  5.27 characters
Reading time:     1.0 minutes
==================================================

MOST COMMON WORDS
------------------------------
 1. the              15 occurrences
 2. and              12 occurrences
 3. to               10 occurrences
 4. of               8 occurrences
 5. a                7 occurrences
------------------------------
```

### Interactive Mode
```
[MEMO] WORD COUNT TOOL
========================================
1. Analyze file
2. Analyze text input
3. Compare files
4. Exit
========================================
Enter your choice (1-4): 1

=== Analyze File ===
Enter filename: my_document.txt
[OK] Analysis complete!
```

### Text Input Mode
```
=== Analyze Text ===
Enter your text (press Enter twice to finish):
The quick brown fox jumps over the lazy dog.
The quick brown fox is fast.

[Analysis results displayed]
```

## Features

### Core Analysis Features
- **Character Count**: Total characters including and excluding spaces
- **Word Count**: Accurate word counting with punctuation handling
- **Line Count**: Counts non-empty lines
- **Paragraph Count**: Identifies paragraphs separated by blank lines
- **Word Frequency**: Calculates frequency of each word
- **Most Common Words**: Shows top N most frequent words
- **Stop Words**: Option to exclude common English stop words
- **Reading Time**: Estimates reading time based on words per minute
- **Average Word Length**: Calculates average word length in characters

### Input Methods
- **File Analysis**: Analyze text files with proper encoding support
- **Direct Input**: Type or paste text directly into the program
- **Command Line**: Analyze files directly from command line
- **Multiple Files**: Compare statistics across multiple files

### Stop Words
The tool excludes common English stop words when requested:
- Articles: a, an, the
- Conjunctions: and, but, or
- Prepositions: at, by, for, from, in, of, on, to
- Pronouns: i, you, he, she, it, we, they
- Common verbs: is, are, was, were, have, has

## Menu Options

1. **Analyze file**: Analyze a text file from disk
2. **Analyze text input**: Type or paste text directly
3. **Compare files**: Compare statistics across multiple files
4. **Exit**: Quit the application

## Command Line Usage

```bash
# Analyze a single file
python word_count.py document.txt

# Run in interactive mode
python word_count.py
```

## Testing

Run the unit tests:
```bash
python -m pytest test_word_count.py -v
```

Or run with unittest:
```bash
python test_word_count.py
```

## Examples

### File Analysis
```bash
# Create a sample file
echo "Hello world! This is a test file. Hello again, world!" > sample.txt

# Analyze it
python word_count.py sample.txt
```

### Text Comparison
```
3. Compare files
Enter filename 1 (or 'done' to finish): file1.txt
[OK] Added: 150 words, 12 lines
Enter filename 2 (or 'done' to finish): file2.txt
[OK] Added: 200 words, 18 lines
Enter filename 3 (or 'done' to finish): done

File                 Words      Lines      Characters
-------------------------------------------------------
file1.txt            150        12         850
file2.txt            200        18         1,200
```

### Stop Word Analysis
```
Analyze without stop words? (y/n): y

MOST COMMON WORDS (NO STOP WORDS)
------------------------------
 1. hello            3 occurrences
 2. world            2 occurrences
 3. test             1 occurrences
------------------------------
```

## File Support

- **Text Files**: .txt, .md, .py, .js, .html, .css, etc.
- **Encoding**: UTF-8 encoding with proper error handling
- **Error Handling**: Graceful handling of missing files and encoding issues

## Performance

- **Large Files**: Efficiently handles files up to several MB
- **Memory Usage**: Processes text without excessive memory consumption
- **Speed**: Fast analysis using optimized string operations

## Keyboard Controls

- **Ctrl+C**: Exit the application at any time
- **Ctrl+D**: Exit the application at any time
- **Enter twice**: Finish text input in direct input mode

## Output Formats

### Statistics Display
- Formatted tables with thousands separators
- Clear section headers and dividers
- Color-coded information (when supported)

### Word Frequency
- Ranked lists of most common words
- Occurrence counts for each word
- Optional stop word exclusion

## Error Handling

The application handles various error conditions:
- **File Not Found**: Clear error messages for missing files
- **Encoding Issues**: Handles non-text files gracefully
- **Empty Input**: Provides feedback for empty text or files
- **Invalid Input**: Validates user input and provides guidance

## Use Cases

- **Writing Analysis**: Analyze essays, articles, or documents
- **Code Analysis**: Count lines in source code files
- **Content Review**: Check word counts for assignments
- **SEO Analysis**: Analyze web content for keyword density
- **Reading Time**: Estimate how long it will take to read documents

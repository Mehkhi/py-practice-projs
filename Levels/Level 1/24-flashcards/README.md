# Flashcards Study App

A simple command-line flashcards application for studying. Load flashcards from a JSON file and track your score as you practice.

## What it does

- Loads flashcards from a JSON file
- Displays questions one by one
- Checks your answers (case-insensitive)
- Tracks your score and shows results at the end
- Provides encouraging feedback based on your performance

## How to run

### Basic usage
```bash
python flashcards.py
```

This will load flashcards from `flashcards.json` in the same directory.

### Using a custom flashcards file
```bash
python flashcards.py my_flashcards.json
```

## Example usage

```
[GRADUATION] Flashcards Study App
==============================
Loaded 10 flashcards from 'flashcards.json'.

Starting study session with 10 flashcards...
Type 'quit' at any time to exit.

Question 1/10:
Q: What is the capital of France?
A: Paris
[OK] Correct!
--------------------------------------------------
Question 2/10:
Q: What is 2 + 2?
A: 5
[X] Incorrect. The correct answer is: 4
--------------------------------------------------
...

==================================================
Quiz Complete!
Score: 8/10 (80.0%)
Good job! [THUMBS UP]
==================================================
```

## Flashcard file format

Create a JSON file with flashcards in this format:

```json
[
  {
    "question": "What is the capital of France?",
    "answer": "Paris"
  },
  {
    "question": "What is 2 + 2?",
    "answer": "4"
  }
]
```

## Features

- **Case-insensitive answers**: "PARIS", "paris", and "Paris" are all correct
- **Whitespace handling**: Extra spaces are automatically trimmed
- **Early exit**: Type 'quit' to exit at any time
- **Score tracking**: See your progress and get encouraging feedback
- **Random order**: Flashcards are shuffled for variety
- **Error handling**: Graceful handling of missing or invalid files

## Testing

Run the included tests to verify everything works:

```bash
python test_flashcards.py
```

## Requirements

- Python 3.7 or higher
- No external dependencies (uses only standard library)

## File structure

```
24-flashcards/
├── flashcards.py          # Main application
├── flashcards.json        # Sample flashcards file
├── test_flashcards.py     # Unit tests
├── README.md             # This file
├── CHECKLIST.md          # Feature checklist
└── SPEC.md               # Project specification
```

## Tips for studying

1. **Create your own flashcards**: Replace `flashcards.json` with your own study material
2. **Practice regularly**: Run the app frequently to reinforce learning
3. **Don't worry about perfect scores**: Focus on learning, not perfection
4. **Use 'quit' strategically**: Exit early if you need to take a break

## Troubleshooting

- **File not found**: Make sure `flashcards.json` exists in the same directory
- **Invalid JSON**: Check that your JSON file has proper syntax
- **Empty flashcards**: Ensure your JSON file contains at least one flashcard

Enjoy studying! [BOOKS][SPARKLES]

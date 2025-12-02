# Guess the Number Game

A command-line number guessing game with multiple difficulty levels, scoring system, and leaderboard functionality.

## What This Project Does

This is a comprehensive number guessing game that demonstrates Python fundamentals including:
- User input and output handling
- Random number generation
- Control flow (if/else, loops)
- Functions and code organization
- File I/O for persistent storage
- Error handling and input validation
- Object-oriented programming concepts

## Features

### Required Features (complete)
- **Random number generation in range** - Generates numbers based on difficulty level
- **Input validation with re-prompting** - Robust input validation with clear error messages
- **Higher/lower hints** - Provides helpful hints after each guess
- **Attempt counting and display** - Tracks and displays remaining attempts

### Bonus Features (complete)
- **Best score persistence to file** - Saves game history and scores to JSON files
- **Difficulty levels** - Four difficulty levels with different ranges and attempt limits
- **Leaderboard with multiple players** - Tracks top 10 players with scores and dates

## How to Run

1. **Prerequisites**: Python 3.7 or higher
2. **Run the game**:
   ```bash
   python guess_the_number.py
   ```
3. **Run tests**:
   ```bash
   python test_guess_the_number.py
   ```

## Example Usage

```
Welcome to Guess the Number!
Try to guess the secret number within the given attempts!

=== GUESS THE NUMBER GAME ===
1. Play Game
2. Change Difficulty
3. View Leaderboard
4. View Statistics
5. Show Difficulty Levels
6. Quit
==============================
Enter your choice (1-6): 1

=== GUESS THE NUMBER ===
Difficulty: Medium
Range: 1 to 50
Attempts: 7
=========================

Attempts left: 7
Enter your guess (1-50): 25
Too high! Try a lower number.

Attempts left: 6
Enter your guess (1-50): 15
Too low! Try a higher number.

Attempts left: 5
Enter your guess (1-50): 20
Too low! Try a higher number.

Attempts left: 4
Enter your guess (1-50): 22
Congratulations! You won!
Score: 45 points
Attempts used: 4
Enter your name for the leaderboard (or press Enter to skip): Alice
Added Alice to leaderboard!
```

## Difficulty Levels

| Level   | Range    | Max Attempts | Multiplier |
|---------|----------|--------------|------------|
| Easy    | 1-10     | 5            | 1x         |
| Medium  | 1-50     | 7            | 2x         |
| Hard    | 1-100    | 10           | 3x         |
| Expert  | 1-1000   | 15           | 5x         |

## Scoring System

- **Base Score**: Range size (max - min + 1)
- **Difficulty Multiplier**: Easy (1x), Medium (2x), Hard (3x), Expert (5x)
- **Attempt Penalty**: Score decreases with more attempts used
- **Final Score**: `(Base Score x Multiplier) / (Attempts Used + 1)`

## Game Menu Options

1. **Play Game** - Start a new game with current difficulty
2. **Change Difficulty** - Select from Easy, Medium, Hard, or Expert
3. **View Leaderboard** - See top 10 players and their scores
4. **View Statistics** - View your personal game statistics
5. **Show Difficulty Levels** - Display all difficulty options
6. **Quit** - Exit the game

## Commands and Input

### During Gameplay
- Enter numbers within the specified range
- Invalid input will prompt for re-entry
- Game provides hints after each guess
- Shows remaining attempts

### Menu Navigation
- Enter numbers 1-6 to select menu options
- Invalid choices will prompt for re-entry

## Technical Details

### Architecture
- **Object-oriented design** - Uses a `GuessTheNumberGame` class to encapsulate functionality
- **Modular functions** - Each feature is implemented as a separate method
- **Type hints** - Uses Python type annotations for better code clarity
- **Error handling** - Comprehensive input validation and error handling

### File I/O
- **Persistent storage** - Saves game history to `guess_the_number_scores.json`
- **Leaderboard storage** - Saves leaderboard to `guess_the_number_leaderboard.json`
- **Automatic loading** - Restores previous data when the program starts
- **Graceful fallback** - Continues operation even if file operations fail

### Input Validation
- **Number validation** - Validates numeric input within specified ranges
- **Range checking** - Ensures guesses are within difficulty level bounds
- **Error messages** - Clear, user-friendly error messages for invalid input

## Testing

The project includes comprehensive unit tests covering:
- Difficulty level configurations
- Secret number generation
- Input validation
- Hint generation
- Score calculation
- Leaderboard functionality
- File operations

Run tests with:
```bash
python test_guess_the_number.py
```

## Learning Objectives Achieved

This project demonstrates mastery of:
1. **Python syntax and semantics** - Proper use of classes, methods, and control structures
2. **User input handling** - Robust input validation and error handling
3. **Control flow** - Effective use of if/else statements and loops
4. **Function organization** - Well-structured, modular code
5. **Error handling** - Graceful handling of edge cases and invalid input
6. **Data structures** - Effective use of lists, dictionaries, and strings
7. **File I/O** - Reading from and writing to JSON files
8. **Random number generation** - Using Python's random module
9. **Code quality** - Clear variable names, consistent formatting, and documentation

## Code Quality Features

- **Consistent formatting** - Follows PEP 8 style guidelines
- **Comprehensive documentation** - Docstrings for all methods
- **Type hints** - Python type annotations throughout
- **Error messages** - Clear, user-friendly error messages
- **Modular design** - Separation of concerns with focused methods
- **Unit tests** - Comprehensive test coverage for core functionality
- **Persistent data** - Automatic save/load of game state

## Game Features

### Core Gameplay
- Random number generation within specified ranges
- Attempt tracking and display
- Higher/lower hints after each guess
- Win/lose detection with appropriate messaging

### Advanced Features
- Multiple difficulty levels with different ranges and attempt limits
- Scoring system based on difficulty and efficiency
- Persistent leaderboard with top 10 players
- Game history tracking with statistics
- Menu-driven interface for easy navigation

### User Experience
- Clear prompts and instructions
- Helpful error messages for invalid input
- Celebration messages for wins
- Encouraging messages for losses
- Easy difficulty selection and game management

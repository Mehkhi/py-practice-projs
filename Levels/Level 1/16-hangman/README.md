# Hangman Game

A command-line implementation of the classic Hangman word guessing game with categories, difficulty levels, and ASCII art.

## Features

### Core Features
- **Word Guessing**: Try to guess words letter by letter
- **Visual Feedback**: ASCII hangman drawing that progresses with wrong guesses
- **Input Validation**: Ensures valid letter input and prevents duplicate guesses
- **Game Status**: Real-time display of word progress, guessed letters, and remaining attempts
- **Win/Lose Detection**: Automatic detection of game completion conditions

### Bonus Features
- **Word Categories**: Choose from 4 different categories:
  - Animals (elephant, giraffe, penguin, etc.)
  - Countries (australia, brazil, canada, etc.)
  - Fruits (apple, banana, cherry, etc.)
  - Sports (basketball, cricket, football, etc.)
- **Difficulty Levels**: 3 difficulty settings:
  - Easy: 8 attempts
  - Medium: 6 attempts
  - Hard: 4 attempts
- **ASCII Art**: Progressive hangman drawing with 8 stages
- **Category Selection**: Choose specific category or random selection
- **Game Statistics**: Track guessed letters and remaining attempts

## How to Run

```bash
python hangman.py
```

## How to Play

1. **Start the Game**: Run the program and follow the prompts
2. **Select Category**: Choose a word category or let the game pick randomly
3. **Select Difficulty**: Choose your difficulty level (Easy, Medium, or Hard)
4. **Guess Letters**: Enter one letter at a time to guess the word
5. **Win Condition**: Guess all letters before running out of attempts
6. **Lose Condition**: Use all attempts before guessing the word

### Game Controls
- Enter a single letter (A-Z) when prompted
- Type 'y' or 'yes' to play again after a game ends
- Type 'n' or 'no' to quit the game

## Game Display

The game shows:
- **Category**: Current word category
- **Word Progress**: Underscores for unguessed letters, revealed letters for correct guesses
- **Guessed Letters**: List of all letters you've tried
- **Attempts Remaining**: How many wrong guesses you have left
- **Hangman Drawing**: ASCII art that progresses with each wrong guess

### Example Game Display

```
Category: Animals
Word: _ _ _ _ _ _ _
Guessed letters: A, E, I, O, U
Attempts remaining: 3/6

   -----
   |   |
   O   |
  /|\  |
  /    |
        |
 =========
```

## Game Rules

1. You must guess one letter at a time
2. Each correct guess reveals all instances of that letter in the word
3. Each wrong guess adds a body part to the hangman
4. The game ends when you either:
   - Guess all letters correctly (WIN)
   - Run out of attempts (LOSE)
5. Letters are case-insensitive

## Word Lists

### Animals (15 words)
elephant, giraffe, penguin, dolphin, butterfly, crocodile, kangaroo, octopus, peacock, rhinoceros, squirrel, tortoise, cheetah, gorilla, hamster

### Countries (15 words)
australia, brazil, canada, denmark, ethiopia, france, germany, hungary, india, jamaica, kenya, luxembourg, mexico, norway, portugal

### Fruits (15 words)
apple, banana, cherry, dragonfruit, elderberry, fig, grape, honeydew, kiwi, lemon, mango, orange, papaya, quince, raspberry

### Sports (15 words)
basketball, cricket, football, golf, hockey, tennis, volleyball, baseball, swimming, cycling, boxing, skiing, surfing, climbing, fencing

## Difficulty Levels

| Level | Attempts | Description |
|-------|----------|-------------|
| Easy | 8 | More forgiving, great for beginners |
| Medium | 6 | Balanced gameplay |
| Hard | 4 | Challenging, for experienced players |

## ASCII Hangman Stages

The game features 8 progressive stages of the hangman drawing:

1. Empty gallows
2. Head added
3. Body added
4. Left arm added
5. Right arm added
6. Left leg added
7. Right leg added
8. Game over display

## Testing

Run the unit tests to verify functionality:

```bash
python -m pytest test_hangman.py -v
```

The test suite includes:
- **25 test methods** covering all game functionality
- **Initialization tests** for proper game setup
- **Word selection tests** for categories and randomization
- **Game logic tests** for guess processing and validation
- **Win/lose condition tests** for game state management
- **Difficulty level tests** for gameplay variations
- **Integration tests** for complete game workflows

## Code Structure

### Main Classes
- `HangmanGame`: Core game class containing all game logic and state

### Key Methods
- `start_new_game()`: Initialize a new game with category and difficulty
- `make_guess()`: Process player guesses with validation
- `check_win_condition()`: Check if player has won
- `check_lose_condition()`: Check if player has lost
- `get_word_progress()`: Display current word progress
- `get_hangman_display()`: Get appropriate ASCII art stage

### Helper Functions
- `display_welcome()`: Show welcome message and instructions
- `display_game_status()`: Show current game state
- `get_player_guess()`: Get and validate player input
- `select_category()`: Handle category selection
- `select_difficulty()`: Handle difficulty selection

## Error Handling

The game includes comprehensive error handling for:
- Invalid input (non-letters, multiple characters)
- Empty input
- Duplicate guesses
- Invalid menu selections
- Case sensitivity (automatically handled)

## Example Gameplay Session

```
============================================================
[TARGET] HANGMAN GAME [TARGET]
============================================================
Welcome to Hangman! Try to guess the word letter by letter.
You have limited attempts before the hangman is complete!
============================================================

Available categories:
1. animals
2. countries
3. fruits
4. sports
5. Random category

Select category (1-5): 1

Difficulty levels:
1. Easy (8 attempts)
2. Medium (6 attempts)
3. Hard (4 attempts)

Select difficulty (1-3): 2

Starting new game...
Category: animals
Difficulty: Medium (6 attempts)
Word has 8 letters

Category: Animals
Word: _ _ _ _ _ _ _ _
Guessed letters: None
Attempts remaining: 6/6

   -----
   |   |
       |
       |
       |
       |
=========

Enter your guess (A-Z): E

Good guess! 'E' is in the word

Category: Animals
Word: _ _ _ _ _ E _ _
Guessed letters: E
Attempts remaining: 6/6

   -----
   |   |
       |
       |
       |
       |
=========

Enter your guess (A-Z): A

Good guess! 'A' is in the word

... (game continues) ...

==================================================
[CELEBRATION] CONGRATULATIONS! YOU WON! [CELEBRATION]
You successfully guessed the word: ELEPHANT
==================================================
```

## Requirements

- Python 3.6 or higher
- No external dependencies required

## File Structure

```
16-hangman/
├── hangman.py              # Main game implementation
├── test_hangman.py         # Unit tests
├── README.md              # This file
├── SPEC.md                # Project specifications
└── CHECKLIST.md           # Project checklist
```

Enjoy playing Hangman! [TARGET]

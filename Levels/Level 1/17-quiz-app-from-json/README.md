# Quiz App from JSON

A command-line quiz application that loads questions from JSON files, presents them to users with optional time limits, and tracks quiz history with detailed results.

## Features

### Core Features
- **JSON Question Loading**: Load quiz questions from structured JSON files
- **Sequential Question Presentation**: Present questions one at a time in order
- **Answer Validation**: Check user answers with case-insensitive comparison
- **Score Calculation**: Calculate and display final scores with percentages
- **Multiple Choice Support**: Handle both multiple choice and text-based questions

### Bonus Features
- **Time Limits**: Optional time limits per question (configurable)
- **Results History**: Save and view quiz results history in JSON format
- **Sample File Generation**: Create sample question files for testing
- **Performance Feedback**: Provide performance-based messages
- **Answer Breakdown**: Show detailed breakdown of correct/incorrect answers
- **Category Support**: Organize questions by categories
- **Interactive Menu**: User-friendly menu system for navigation

## How to Run

```bash
python quiz_app_from_json.py
```

## How to Use

### 1. Main Menu Options
When you start the app, you'll see the main menu:

```
[CLIPBOARD] MAIN MENU [CLIPBOARD]
1. Load questions from file
2. Create sample questions file
3. Start quiz
4. View quiz history
5. Set time limit per question
6. Exit
```

### 2. Creating Questions
First, create a JSON file with your questions. You can use option 2 to create a sample file, or create your own:

#### JSON Format Options

**Option 1: List format**
```json
[
  {
    "question": "What is the capital of France?",
    "options": ["London", "Berlin", "Paris", "Madrid"],
    "correct_answer": "Paris",
    "category": "Geography"
  },
  {
    "question": "What is 2 + 2?",
    "options": ["3", "4", "5", "6"],
    "correct_answer": "4",
    "category": "Mathematics"
  }
]
```

**Option 2: Dictionary format**
```json
{
  "questions": [
    {
      "question": "Which planet is known as the Red Planet?",
      "options": ["Venus", "Mars", "Jupiter", "Saturn"],
      "correct_answer": "Mars",
      "category": "Science"
    }
  ]
}
```

### 3. Question Fields

- **question** (required): The question text
- **correct_answer** (required): The correct answer
- **options** (optional): List of multiple choice options
- **category** (optional): Question category for organization

### 4. Taking a Quiz

1. Load questions from a file (Option 1)
2. Start the quiz (Option 3)
3. Answer each question:
   - For multiple choice: Enter the number (1, 2, 3, 4) or the text
   - For text questions: Type your answer directly
4. View your results at the end
5. Choose to save results to history

### 5. Time Limits

Set custom time limits per question (Option 5):
- Default: 30 seconds per question
- Minimum: 5 seconds
- Enter any value in seconds

## Example Usage Session

```
============================================================
[TARGET] QUIZ APP FROM JSON [TARGET]
============================================================
Welcome to the Quiz App! Test your knowledge with questions
loaded from JSON files. Track your progress and improve!
============================================================

[CLIPBOARD] MAIN MENU [CLIPBOARD]
1. Load questions from file
2. Create sample questions file
3. Start quiz
4. View quiz history
5. Set time limit per question
6. Exit

Enter your choice (1-6): 2
Enter filename (default: sample_questions.json): my_quiz.json
Sample questions file 'my_quiz.json' created successfully.

Enter your choice (1-6): 1

Available question files:
1. my_quiz.json

Select file (1-1): 1
[OK] Successfully loaded 5 questions from 'my_quiz.json'

Enter your choice (1-6): 3

[TARGET] QUIZ STARTED [TARGET]
Total questions: 5
Time limit per question: 30 seconds
Good luck!

============================================================
Question 1 of 5
Category: Geography
============================================================

What is the capital of France?

1. London
2. Berlin
3. Paris
4. Madrid

Time limit: 30 seconds
Your answer (enter number or text): 3
[OK] Correct!

Press Enter to continue...

============================================================
Question 2 of 5
Category: Mathematics
============================================================

What is 2 + 2?

1. 3
2. 4
3. 5
4. 6

Time limit: 30 seconds
Your answer (enter number or text): 2
[OK] Correct!

... (quiz continues) ...

============================================================
[TARGET] QUIZ RESULTS [TARGET]
============================================================
Score: 4/5
Percentage: 80.0%
Duration: 45.2 seconds
Completed: 2023-12-07T15:30:45.123456
[STAR] Excellent work!

============================================================
ANSWER BREAKDOWN
============================================================
[OK] Q1: What is the capital of France?...
[X] Q3: Which planet is known as the Red Planet?...
   Your answer: Venus
   Correct answer: Mars

Save results to file? (y/n): y
Results saved to 'quiz_results.json'
```

## Quiz Results

### Performance Messages
- **90%+**: [TROPHY] Outstanding performance!
- **80-89%**: [STAR] Excellent work!
- **70-79%**: [THUMBS UP] Good job!
- **60-69%**: [BOOKS] Not bad, keep studying!
- **Below 60%**: [FLEX] Keep practicing!

### Results History
View your quiz history (Option 4) to see:
- Quiz scores and percentages
- Time taken for each quiz
- Dates and times of completion
- Performance trends over time

### Results File Format
Results are saved in `quiz_results.json`:
```json
[
  {
    "score": 4,
    "total_questions": 5,
    "percentage": 80.0,
    "duration_seconds": 45.2,
    "start_time": "2023-12-07T15:30:00.123456",
    "end_time": "2023-12-07T15:30:45.123456",
    "answers": [
      {
        "question": "What is the capital of France?",
        "user_answer": "3",
        "correct_answer": "Paris",
        "is_correct": true,
        "question_number": 1
      }
    ]
  }
]
```

## Testing

Run the unit tests to verify functionality:

```bash
python -m pytest test_quiz_app_from_json.py -v
```

The test suite includes:
- **25 test methods** covering all app functionality
- **JSON loading tests** for different file formats
- **Answer validation tests** for various input types
- **Quiz logic tests** for scoring and results
- **File I/O tests** for saving and loading results
- **Integration tests** for complete workflows

## Code Structure

### Main Classes
- `QuizApp`: Core application class containing all quiz logic

### Key Methods
- `load_questions_from_json()`: Load questions from JSON files
- `run_quiz()`: Execute a complete quiz session
- `check_answer()`: Validate user answers
- `get_quiz_results()`: Calculate and format quiz results
- `save_results()`: Save results to history file
- `display_results()`: Show formatted results to user

### Helper Functions
- `display_welcome()`: Show welcome message
- `get_menu_choice()`: Handle main menu navigation
- `select_question_file()`: File selection interface

## Error Handling

The app includes comprehensive error handling for:
- **File Operations**: Missing files, invalid JSON format
- **Input Validation**: Invalid menu choices, non-numeric input
- **Quiz Logic**: Empty questions, missing required fields
- **Time Limits**: Graceful handling of expired time limits
- **Data Integrity**: Corrupted result files

## Sample Question Categories

### Geography
```json
{
  "question": "What is the largest ocean on Earth?",
  "options": ["Atlantic", "Indian", "Arctic", "Pacific"],
  "correct_answer": "Pacific",
  "category": "Geography"
}
```

### Science
```json
{
  "question": "What is the chemical symbol for gold?",
  "options": ["Go", "Gd", "Au", "Ag"],
  "correct_answer": "Au",
  "category": "Science"
}
```

### Mathematics
```json
{
  "question": "What is the square root of 144?",
  "correct_answer": "12",
  "category": "Mathematics"
}
```

### History
```json
{
  "question": "In which year did World War II end?",
  "options": ["1943", "1944", "1945", "1946"],
  "correct_answer": "1945",
  "category": "History"
}
```

## Configuration

### Default Settings
- Time limit per question: 30 seconds
- Results file: `quiz_results.json`
- Minimum time limit: 5 seconds
- Supported file formats: `.json`

### Customization
You can customize:
- Time limits per question
- Question file names and locations
- Results file location
- Question categories and difficulty

## Requirements

- Python 3.7 or higher
- No external dependencies required
- JSON support (built into Python)

## File Structure

```
17-quiz-app-from-json/
├── quiz_app_from_json.py          # Main application
├── test_quiz_app_from_json.py     # Unit tests
├── README.md                      # This file
├── SPEC.md                        # Project specifications
├── CHECKLIST.md                   # Project checklist
├── sample_questions.json          # Sample questions (auto-generated)
└── quiz_results.json              # Results history (auto-generated)
```

## Tips for Creating Questions

1. **Keep questions clear and concise**
2. **Provide unambiguous correct answers**
3. **Use consistent formatting for options**
4. **Include relevant categories for organization**
5. **Test your JSON files before using them**
6. **Mix difficulty levels for engaging quizzes**

## Advanced Usage

### Batch Quiz Creation
Create multiple quiz files for different subjects:
- `science_quiz.json`
- `history_quiz.json`
- `math_quiz.json`

### Progressive Difficulty
Structure questions with increasing difficulty:
- Easy questions first
- Medium difficulty in middle
- Challenging questions at end

### Themed Quizzes
Create themed quizzes for specific topics:
- "Space Exploration"
- "World Capitals"
- "Famous Scientists"

Enjoy testing your knowledge with the Quiz App! [TARGET]

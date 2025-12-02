# Rule-Based Chatbot

A sophisticated rule-based chatbot built with Python that demonstrates pattern matching, context tracking, and sentiment analysis. This project showcases professional Python development practices including modular architecture, comprehensive testing, and proper error handling.

## Features

### Core Features
- **Pattern Matching**: Advanced regex-based pattern matching for various input types
- **Response Templates**: Dynamic response generation with variable substitution
- **Context Tracking**: Remembers user names, previous topics, and conversation history
- **Sentiment Analysis**: Basic keyword-based sentiment scoring
- **Session Logging**: Complete conversation analytics and logging
- **Fallback Responses**: Intelligent responses for unmatched input

### Supported Interaction Types
- **Greetings**: Hello, hi, hey, good morning, etc.
- **Farewells**: Bye, goodbye, see you, take care, etc.
- **Questions**: Any question-based input
- **Name Extraction**: "My name is...", "I'm...", "Call me..."
- **Help Requests**: "help", "what can you do", etc.
- **How Are You**: Various ways to ask about wellbeing

### Bonus Features
- **Custom Configuration**: JSON-based rule configuration system
- **Sentiment Analysis**: Positive/negative keyword scoring
- **Conversation Analytics**: Detailed session statistics and logging
- **CLI Interface**: Full command-line interface with multiple modes

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Setup

1. **Clone or download the project**
   ```bash
   cd 12-rule-based-chatbot
   ```

2. **Create virtual environment (recommended)**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

   Note: The core chatbot uses only Python standard library modules. Additional dependencies are optional for development.

## Usage

### Interactive Mode (Default)
Start a conversation with the chatbot:

```bash
python -m rule_based_chatbot
```

Example conversation:
```
🤖 Rule-Based Chatbot
Type 'quit', 'exit', or 'bye' to end the conversation.
Type 'help' to see what I can do!
--------------------------------------------------
You: hello
Chatbot: Hello! How can I help you today?
You: my name is Alice
Chatbot: Nice to meet you, Alice!
You: how are you?
Chatbot: I'm doing great, thanks for asking! How about you?
You: bye
Chatbot: Goodbye! Have a great day! 👋
```

### Single Message Mode
Process a single message and get a response:

```bash
python -m rule_based_chatbot -m "Hello, how are you?"
```

### Custom Configuration
Use custom rules from a JSON configuration file:

```bash
python -m rule_based_chatbot --config rules.json
```

### Verbose Logging
Enable detailed logging for debugging:

```bash
python -m rule_based_chatbot -v
```

### Show Statistics
Display conversation statistics:

```bash
python -m rule_based_chatbot --stats
```

## Configuration

### Custom Rules
Create a JSON file with custom rules to extend the chatbot's capabilities:

```json
{
  "weather": {
    "patterns": [
      r".*(weather|temperature|rain|sunny|cloudy|forecast).*"
    ],
    "responses": [
      "I don't have access to real-time weather data, but I hope it's nice where you are!"
    ]
  },
  "jokes": {
    "patterns": [
      r".*(joke|funny|laugh|humor).*"
    ],
    "responses": [
      "Why don't scientists trust atoms? Because they make up everything!"
    ]
  }
}
```

### Rule Structure
Each rule category contains:
- `patterns`: Array of regex patterns to match
- `responses`: Array of possible responses (randomly selected)

### Variable Substitution
Responses can include variables:
- `{name}`: User's name (if known)
- `{1}`, `{2}`, etc.: Regex capture groups

## Development

### Project Structure
```
12-rule-based-chatbot/
├── rule_based_chatbot/          # Package directory
│   ├── __init__.py             # Package initialization
│   ├── __main__.py             # Package entry point
│   ├── main.py                 # CLI interface
│   └── core.py                 # Core chatbot logic
├── tests/                      # Test suite
│   ├── __init__.py
│   └── test_rule_based_chatbot.py
├── requirements.txt            # Dependencies
├── rules.json                  # Sample custom rules
├── README.md                   # This file
├── CHECKLIST.md                # Feature checklist
└── SPEC.md                     # Project specification
```

### Running Tests
Execute the comprehensive test suite:

```bash
pytest tests/ -v
```

### Code Quality
Format code with Black:
```bash
black rule_based_chatbot/
```

Lint code with Ruff:
```bash
ruff check rule_based_chatbot/
```

## API Reference

### Core Classes

#### `ChatContext`
Stores conversation state and user information.

**Attributes:**
- `user_name` (Optional[str]): User's name
- `previous_topic` (Optional[str]): Last conversation topic
- `message_count` (int): Number of messages exchanged
- `sentiment_score` (float): Current sentiment score
- `session_start` (datetime): Session start time

#### `RuleBasedChatbot`
Main chatbot class with pattern matching and context tracking.

**Methods:**
- `get_response(user_input: str) -> str`: Generate response for user input
- `get_context() -> Dict[str, Any]`: Get current conversation context
- `get_conversation_log() -> List[Dict]`: Get complete conversation history
- `reset_context() -> None`: Reset conversation state

## Examples

### Basic Conversation
```python
from rule_based_chatbot.core import RuleBasedChatbot

chatbot = RuleBasedChatbot()
response = chatbot.get_response("Hello, my name is John")
print(response)  # "Nice to meet you, John!"
```

### Custom Configuration
```python
from rule_based_chatbot.core import RuleBasedChatbot

chatbot = RuleBasedChatbot(config_file="custom_rules.json")
response = chatbot.get_response("What's the weather like?")
print(response)
```

### Conversation Analytics
```python
from rule_based_chatbot.core import RuleBasedChatbot

chatbot = RuleBasedChatbot()

# Have a conversation
chatbot.get_response("hello")
chatbot.get_response("my name is Alice")

# Get analytics
context = chatbot.get_context()
log = chatbot.get_conversation_log()

print(f"Messages: {context['message_count']}")
print(f"User: {context['user_name']}")
print(f"Sentiment: {context['sentiment_score']}")
```

## Logging

The chatbot automatically logs conversations to:
- Console output (INFO level)
- `chatbot.log` file (for persistent logging)

Enable verbose logging with the `-v` flag for debugging.

## Limitations

- **No Real-time Data**: Cannot access current time, weather, or external APIs
- **Rule-Based**: Limited to predefined patterns and responses
- **Simple Sentiment**: Basic keyword-based sentiment analysis
- **Memory**: Context is lost when the program ends
- **Language**: Primarily designed for English input

## Troubleshooting

### Common Issues

1. **Import Error**: Ensure you're in the project directory and using Python 3.8+
2. **Permission Error**: Check file permissions for log files
3. **Config File Not Found**: Verify the path to custom configuration files
4. **Regex Errors**: Invalid patterns in custom rules will be skipped with warnings

### Debug Mode
Run with verbose logging to troubleshoot issues:

```bash
python -m rule_based_chatbot -v
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

This project is open source and available under the MIT License.

## Acknowledgments

This project demonstrates professional Python development practices including:
- Clean Code principles
- Test-Driven Development
- Modular Architecture
- Comprehensive Error Handling
- Documentation Standards
- Type Hints and Docstrings

---

**Built with ❤️ using Python 3.8+**

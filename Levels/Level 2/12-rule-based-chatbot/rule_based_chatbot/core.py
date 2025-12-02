"""Core chatbot functionality with pattern matching and context tracking."""

import re
import json
import logging
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
from dataclasses import dataclass, field


@dataclass
class ChatContext:
    """Stores conversation context and user information."""
    user_name: Optional[str] = None
    previous_topic: Optional[str] = None
    message_count: int = 0
    sentiment_score: float = 0.0
    session_start: datetime = field(default_factory=datetime.now)


class RuleBasedChatbot:
    """A rule-based chatbot with pattern matching and context tracking."""

    def __init__(self, config_file: Optional[str] = None) -> None:
        """Initialize the chatbot with default or custom rules."""
        self.logger = logging.getLogger(__name__)
        self.context = ChatContext()
        self.rules = self._load_rules(config_file)
        self.sentiment_keywords = self._load_sentiment_keywords()
        self.conversation_log: List[Dict[str, Any]] = []

    def _load_rules(self, config_file: Optional[str] = None) -> Dict[str, Any]:
        """Load chatbot rules from config file or use defaults."""
        default_rules = {
            "greetings": {
                "patterns": [
                    r"^(hi|hello|hey|good morning|good afternoon|good evening)[\s!?.]*$",
                    r"^(howdy|yo|what's up|sup)[\s!?.]*$"
                ],
                "responses": [
                    "Hello! How can I help you today?",
                    "Hi there! What can I do for you?",
                    "Hey! How are you doing?"
                ]
            },
            "farewells": {
                "patterns": [
                    r"^(bye|goodbye|see you|later|cya|farewell)[\s!?.]*$",
                    r"^(have a good day|take care|see you later)[\s!?.]*$"
                ],
                "responses": [
                    "Goodbye! Have a great day!",
                    "See you later! Take care!",
                    "Bye! It was nice talking to you!"
                ]
            },
            "questions": {
                "patterns": [
                    r".*\?$",
                    r"^(what|who|where|when|why|how) .+",
                    r"^(can|could|would|should|will|do|does|did|is|are|am) .+"
                ],
                "responses": [
                    "That's an interesting question. Let me think about it.",
                    "I'm not sure I have the answer, but I'll try to help.",
                    "That's something to consider. What are your thoughts on it?"
                ]
            },
            "name_extraction": {
                "patterns": [
                    r"my name is (\w+)",
                    r"i'm (\w+)",
                    r"i am (\w+)",
                    r"call me (\w+)"
                ],
                "responses": [
                    "Nice to meet you, {name}!",
                    "Hello {name}! It's great to meet you.",
                    "{name}, what a lovely name! How can I help you today?"
                ]
            },
            "how_are_you": {
                "patterns": [
                    r"^(how are you|how do you do|how's it going)[\s!?.]*$",
                    r"^(how have you been|how are things)[\s!?.]*$"
                ],
                "responses": [
                    "I'm doing great, thanks for asking! How about you?",
                    "I'm functioning perfectly! How are you feeling today?",
                    "Everything's running smoothly here! How are things with you?"
                ]
            },
            "help": {
                "patterns": [
                    r"^(help|what can you do|commands|options)[\s!?.]*$",
                    r"^(what do you do|how do you work)[\s!?.]*$"
                ],
                "responses": [
                    "I'm a rule-based chatbot that can chat with you, remember your name, and track our conversation. Try asking me questions or just say hello!",
                    "I can have conversations, remember information about you, and respond to various types of messages. What would you like to talk about?"
                ]
            }
        }

        if config_file:
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    custom_rules = json.load(f)
                    if not isinstance(custom_rules, dict):
                        raise ValueError("Custom rules configuration must be a mapping of categories.")
                    for category, config in custom_rules.items():
                        if not isinstance(config, dict):
                            self.logger.warning(
                                f"Skipping category '{category}' in {config_file}: expected a mapping."
                            )
                            continue
                        patterns = config.get("patterns")
                        responses = config.get("responses")
                        if category in default_rules:
                            if patterns is not None:
                                if isinstance(patterns, list):
                                    default_rules[category]["patterns"].extend(
                                        str(pattern) for pattern in patterns
                                    )
                                else:
                                    self.logger.warning(
                                        f"Ignoring non-list patterns for category '{category}' in {config_file}."
                                    )
                            if responses is not None:
                                if isinstance(responses, list):
                                    default_rules[category]["responses"].extend(
                                        str(response) for response in responses
                                    )
                                else:
                                    self.logger.warning(
                                        f"Ignoring non-list responses for category '{category}' in {config_file}."
                                    )
                        else:
                            if not isinstance(patterns, list) or not isinstance(responses, list):
                                self.logger.warning(
                                    f"Skipping category '{category}' in {config_file}: both 'patterns' and "
                                    "'responses' must be provided as lists."
                                )
                                continue
                            default_rules[category] = {
                                "patterns": [str(pattern) for pattern in patterns],
                                "responses": [str(response) for response in responses]
                            }
                    self.logger.info(f"Loaded custom rules from {config_file}")
            except (FileNotFoundError, json.JSONDecodeError, ValueError) as e:
                self.logger.warning(f"Could not load config file {config_file}: {e}")

        return default_rules

    def _load_sentiment_keywords(self) -> Dict[str, float]:
        """Load sentiment keywords for basic sentiment analysis."""
        return {
            "positive": {
                "good": 1.0, "great": 1.5, "awesome": 2.0, "fantastic": 2.0,
                "wonderful": 2.0, "excellent": 2.0, "amazing": 2.0, "love": 1.5,
                "happy": 1.5, "excited": 1.5, "perfect": 1.5, "best": 1.5,
                "nice": 1.0, "cool": 1.0, "thank": 1.0, "thanks": 1.0
            },
            "negative": {
                "bad": -1.0, "terrible": -2.0, "awful": -2.0, "horrible": -2.0,
                "hate": -2.0, "sad": -1.5, "angry": -1.5, "frustrated": -1.5,
                "worst": -2.0, "poor": -1.0, "wrong": -1.0, "problem": -1.0,
                "issue": -1.0, "difficult": -1.0, "hard": -1.0
            }
        }

    def _calculate_sentiment(self, text: str) -> float:
        """Calculate sentiment score for given text."""
        words = re.findall(r'\b\w+\b', text.lower())
        score = 0.0

        for word in words:
            if word in self.sentiment_keywords["positive"]:
                score += self.sentiment_keywords["positive"][word]
            elif word in self.sentiment_keywords["negative"]:
                score += self.sentiment_keywords["negative"][word]

        return score

    def _match_pattern(self, text: str, patterns: List[str]) -> Optional[re.Match]:
        """Match text against a list of regex patterns."""
        for pattern in patterns:
            try:
                match = re.match(pattern, text, re.IGNORECASE)
                if match:
                    return match
            except re.error as e:
                self.logger.warning(f"Invalid regex pattern '{pattern}': {e}")
        return None

    def _substitute_variables(self, response: str, match_groups: Tuple[str, ...] = ()) -> str:
        """Substitute variables in response templates."""
        response = response.replace("{name}", self.context.user_name or "there")

        if match_groups:
            for i, group in enumerate(match_groups):
                response = response.replace(f"{{{i+1}}}", group)

        return response

    def _log_conversation(self, user_input: str, bot_response: str, category: str) -> None:
        """Log conversation for analytics."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "user_input": user_input,
            "bot_response": bot_response,
            "category": category,
            "sentiment_score": self.context.sentiment_score,
            "message_count": self.context.message_count
        }
        self.conversation_log.append(log_entry)
        self.logger.debug(f"Logged conversation: {category}")

    def get_response(self, user_input: str) -> str:
        """Generate response based on user input and current context."""
        if not user_input or not user_input.strip():
            return "Please say something! I'm here to chat."

        original_input = user_input.strip()
        user_input = original_input.lower()
        self.context.message_count += 1
        self.context.sentiment_score = self._calculate_sentiment(user_input)

        # Check each rule category
        for category, rule in self.rules.items():
            match = self._match_pattern(user_input, rule["patterns"])
            if match:
                # Handle name extraction
                if category == "name_extraction" and match.groups():
                    # Extract name from original input to preserve case
                    name_match = self._match_pattern(original_input, rule["patterns"])
                    if name_match and name_match.groups():
                        self.context.user_name = name_match.group(1)

                # Update context
                self.context.previous_topic = category

                # Select response
                import random
                response = random.choice(rule["responses"])
                response = self._substitute_variables(response, match.groups())

                # Log conversation
                self._log_conversation(original_input, response, category)

                return response

        # Fallback response
        fallback_responses = [
            "That's interesting! Tell me more.",
            "I'm not sure how to respond to that. Can you try rephrasing?",
            "Hmm, I don't have a specific response for that. What else would you like to discuss?",
            "I'm still learning! Could you try asking me something else?",
            "That's beyond my current capabilities. How about we talk about something else?"
        ]

        import random
        response = random.choice(fallback_responses)
        self._log_conversation(original_input, response, "fallback")

        return response

    def get_context(self) -> Dict[str, Any]:
        """Get current conversation context."""
        return {
            "user_name": self.context.user_name,
            "previous_topic": self.context.previous_topic,
            "message_count": self.context.message_count,
            "sentiment_score": self.context.sentiment_score,
            "session_duration": str(datetime.now() - self.context.session_start)
        }

    def get_conversation_log(self) -> List[Dict[str, Any]]:
        """Get the complete conversation log."""
        return self.conversation_log.copy()

    def reset_context(self) -> None:
        """Reset the conversation context."""
        self.context = ChatContext()
        self.conversation_log.clear()
        self.logger.info("Conversation context reset")

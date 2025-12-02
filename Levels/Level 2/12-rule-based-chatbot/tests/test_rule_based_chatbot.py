"""Comprehensive unit tests for the rule-based chatbot."""

import pytest
import tempfile
import json
import os
from datetime import datetime
from rule_based_chatbot.core import RuleBasedChatbot, ChatContext


class TestChatContext:
    """Test cases for ChatContext class."""

    def test_chat_context_initialization(self):
        """Test ChatContext initializes with default values."""
        context = ChatContext()
        assert context.user_name is None
        assert context.previous_topic is None
        assert context.message_count == 0
        assert context.sentiment_score == 0.0
        assert isinstance(context.session_start, datetime)

    def test_chat_context_with_values(self):
        """Test ChatContext initialization with custom values."""
        start_time = datetime.now()
        context = ChatContext(
            user_name="Alice",
            previous_topic="greetings",
            message_count=5,
            sentiment_score=1.5,
            session_start=start_time
        )
        assert context.user_name == "Alice"
        assert context.previous_topic == "greetings"
        assert context.message_count == 5
        assert context.sentiment_score == 1.5
        assert context.session_start == start_time


class TestRuleBasedChatbot:
    """Test cases for RuleBasedChatbot class."""

    def setup_method(self):
        """Setup test fixtures before each test method."""
        self.chatbot = RuleBasedChatbot()

    def test_chatbot_initialization(self):
        """Test chatbot initializes correctly."""
        assert isinstance(self.chatbot.context, ChatContext)
        assert isinstance(self.chatbot.rules, dict)
        assert isinstance(self.chatbot.sentiment_keywords, dict)
        assert isinstance(self.chatbot.conversation_log, list)
        assert len(self.chatbot.rules) > 0
        assert "greetings" in self.chatbot.rules
        assert "farewells" in self.chatbot.rules

    def test_custom_config_loading(self):
        """Test loading custom configuration from file."""
        custom_rules = {
            "test_category": {
                "patterns": [r"test pattern"],
                "responses": ["test response"]
            }
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(custom_rules, f)
            config_file = f.name

        try:
            chatbot = RuleBasedChatbot(config_file=config_file)
            assert "test_category" in chatbot.rules
            assert chatbot.rules["test_category"]["responses"] == ["test response"]
        finally:
            os.unlink(config_file)

    def test_invalid_config_file(self):
        """Test handling of invalid configuration file."""
        chatbot = RuleBasedChatbot(config_file="nonexistent_file.json")
        # Should still work with default rules
        assert "greetings" in chatbot.rules

    def test_partial_custom_config_extends_defaults(self):
        """Custom configs that provide partial overrides should extend defaults."""
        custom_rules = {
            "greetings": {
                "responses": ["Hola!"]
            },
            "farewells": {
                "patterns": [r"adios"],
                "responses": ["Adios!"]
            }
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(custom_rules, f)
            config_file = f.name

        try:
            chatbot = RuleBasedChatbot(config_file=config_file)
            greeting_responses = chatbot.rules["greetings"]["responses"]
            assert "Hola!" in greeting_responses
            farewell_patterns = chatbot.rules["farewells"]["patterns"]
            assert any("adios" in pattern for pattern in farewell_patterns)
        finally:
            os.unlink(config_file)

    def test_invalid_custom_rule_entries_are_skipped(self):
        """Invalid custom rule entries should be ignored without breaking defaults."""
        custom_rules = {
            "greetings": "not-a-dict",
            "farewells": {
                "patterns": "not-a-list",
                "responses": ["Bye"]
            },
            "new_category": {
                "patterns": [r"valid"]
            }
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(custom_rules, f)
            config_file = f.name

        try:
            chatbot = RuleBasedChatbot(config_file=config_file)
            assert chatbot.rules["greetings"]["patterns"]
            assert chatbot.rules["farewells"]["responses"]
            assert "new_category" not in chatbot.rules
        finally:
            os.unlink(config_file)

    def test_greeting_responses(self):
        """Test greeting pattern matching and responses."""
        greetings = ["hello", "hi", "hey", "good morning", "what's up"]

        for greeting in greetings:
            response = self.chatbot.get_response(greeting)
            assert isinstance(response, str)
            assert len(response) > 0
            # Should be a greeting response
            assert any(word in response.lower() for word in ["hello", "hi", "hey", "help"])

    def test_farewell_responses(self):
        """Test farewell pattern matching and responses."""
        farewells = ["bye", "goodbye", "see you", "later", "take care"]

        for farewell in farewells:
            response = self.chatbot.get_response(farewell)
            assert isinstance(response, str)
            assert len(response) > 0
            # Should be a farewell response
            assert any(word in response.lower() for word in ["goodbye", "see you", "take care", "bye"])

    def test_question_responses(self):
        """Test question pattern matching and responses."""
        questions = [
            "how are you?",
            "what is your name?",
            "where do you live?",
            "can you help me?"
        ]

        for question in questions:
            response = self.chatbot.get_response(question)
            assert isinstance(response, str)
            assert len(response) > 0

    def test_name_extraction(self):
        """Test name extraction and context updates."""
        name_inputs = [
            "my name is Alice",
            "I'm Bob",
            "I am Charlie",
            "call me David"
        ]

        expected_names = ["Alice", "Bob", "Charlie", "David"]

        for name_input, expected_name in zip(name_inputs, expected_names):
            response = self.chatbot.get_response(name_input)
            assert self.chatbot.context.user_name == expected_name
            assert expected_name in response

    def test_how_are_you_responses(self):
        """Test how are you pattern matching."""
        how_are_you_inputs = [
            "how are you",
            "how's it going",
            "how have you been"
        ]

        for input_text in how_are_you_inputs:
            response = self.chatbot.get_response(input_text)
            assert isinstance(response, str)
            assert len(response) > 0

    def test_help_responses(self):
        """Test help pattern matching."""
        help_inputs = [
            "help",
            "what can you do",
            "commands",
            "how do you work"
        ]

        for input_text in help_inputs:
            response = self.chatbot.get_response(input_text)
            assert isinstance(response, str)
            assert len(response) > 0

    def test_fallback_responses(self):
        """Test fallback responses for unmatched input."""
        unmatched_inputs = [
            "xyz123",
            "random text that doesn't match anything",
            "42",
            "completely unrelated phrase"
        ]

        for input_text in unmatched_inputs:
            response = self.chatbot.get_response(input_text)
            assert isinstance(response, str)
            assert len(response) > 0
            # Should be a fallback response
            assert any(phrase in response.lower() for phrase in ["interesting", "not sure", "beyond", "capabilities", "rephrasing", "don't have", "specific response", "discuss", "learning"])

    def test_empty_input(self):
        """Test handling of empty input."""
        response = self.chatbot.get_response("")
        assert isinstance(response, str)
        assert len(response) > 0
        assert "please say something" in response.lower()

        response = self.chatbot.get_response("   ")
        assert isinstance(response, str)
        assert len(response) > 0

    def test_context_tracking(self):
        """Test conversation context tracking."""
        # Send a greeting
        self.chatbot.get_response("hello")
        assert self.chatbot.context.previous_topic == "greetings"
        assert self.chatbot.context.message_count == 1

        # Send name
        self.chatbot.get_response("my name is Alice")
        assert self.chatbot.context.user_name == "Alice"
        assert self.chatbot.context.previous_topic == "name_extraction"
        assert self.chatbot.context.message_count == 2

    def test_sentiment_analysis(self):
        """Test sentiment analysis functionality."""
        # Positive sentiment
        positive_text = "I am feeling great and awesome today"
        score = self.chatbot._calculate_sentiment(positive_text)
        assert score > 0

        # Negative sentiment
        negative_text = "This is terrible and awful"
        score = self.chatbot._calculate_sentiment(negative_text)
        assert score < 0

        # Neutral sentiment
        neutral_text = "The sky is blue"
        score = self.chatbot._calculate_sentiment(neutral_text)
        assert score == 0

    def test_conversation_logging(self):
        """Test conversation logging functionality."""
        # Send some messages
        self.chatbot.get_response("hello")
        self.chatbot.get_response("my name is Alice")
        self.chatbot.get_response("how are you?")

        log = self.chatbot.get_conversation_log()
        assert len(log) == 3

        # Check log entry structure
        for entry in log:
            assert "timestamp" in entry
            assert "user_input" in entry
            assert "bot_response" in entry
            assert "category" in entry
            assert "sentiment_score" in entry
            assert "message_count" in entry

    def test_get_context(self):
        """Test getting conversation context."""
        # Add some conversation
        self.chatbot.get_response("hello")
        self.chatbot.get_response("my name is Alice")

        context = self.chatbot.get_context()
        assert isinstance(context, dict)
        assert "user_name" in context
        assert "previous_topic" in context
        assert "message_count" in context
        assert "sentiment_score" in context
        assert "session_duration" in context

        assert context["user_name"] == "Alice"
        assert context["message_count"] == 2

    def test_reset_context(self):
        """Test resetting conversation context."""
        # Add some conversation
        self.chatbot.get_response("hello")
        self.chatbot.get_response("my name is Alice")

        # Reset context
        self.chatbot.reset_context()

        # Check context is reset
        assert self.chatbot.context.user_name is None
        assert self.chatbot.context.previous_topic is None
        assert self.chatbot.context.message_count == 0
        assert self.chatbot.context.sentiment_score == 0.0
        assert len(self.chatbot.conversation_log) == 0

    def test_variable_substitution(self):
        """Test variable substitution in responses."""
        # Test with no name
        response = self.chatbot._substitute_variables("Hello {name}!")
        assert response == "Hello there!"

        # Test with name set
        self.chatbot.context.user_name = "Alice"
        response = self.chatbot._substitute_variables("Hello {name}!")
        assert response == "Hello Alice!"

        # Test with match groups
        response = self.chatbot._substitute_variables("Hello {1}!", ("Bob",))
        assert response == "Hello Bob!"

    def test_pattern_matching(self):
        """Test regex pattern matching."""
        patterns = [r"hello", r"my name is (\w+)", r"\d+"]

        # Test matching patterns
        assert self.chatbot._match_pattern("hello", patterns) is not None
        assert self.chatbot._match_pattern("my name is Alice", patterns) is not None
        assert self.chatbot._match_pattern("123", patterns) is not None

        # Test non-matching pattern
        assert self.chatbot._match_pattern("goodbye", patterns) is None

    def test_invalid_regex_patterns(self):
        """Test handling of invalid regex patterns."""
        # This should not crash the chatbot
        invalid_patterns = [r"[invalid regex", r"*invalid*"]

        # Should return None for invalid patterns
        assert self.chatbot._match_pattern("test", invalid_patterns) is None

    def test_message_count_increment(self):
        """Test message count increments correctly."""
        initial_count = self.chatbot.context.message_count

        self.chatbot.get_response("hello")
        assert self.chatbot.context.message_count == initial_count + 1

        self.chatbot.get_response("how are you?")
        assert self.chatbot.context.message_count == initial_count + 2

    def test_case_insensitive_matching(self):
        """Test that pattern matching is case insensitive."""
        responses = []
        test_inputs = ["Hello", "HELLO", "hello", "HeLLo"]

        for input_text in test_inputs:
            response = self.chatbot.get_response(input_text)
            responses.append(response)

        # All should trigger greeting responses
        for response in responses:
            assert isinstance(response, str)
            assert len(response) > 0


class TestIntegration:
    """Integration tests for the complete chatbot system."""

    def test_full_conversation_flow(self):
        """Test a complete conversation flow."""
        chatbot = RuleBasedChatbot()

        # Start conversation
        response1 = chatbot.get_response("hello")
        assert chatbot.context.previous_topic == "greetings"

        # Introduce self
        response2 = chatbot.get_response("my name is Alice")
        assert chatbot.context.user_name == "Alice"
        assert "Alice" in response2

        # Ask question
        response3 = chatbot.get_response("how are you?")
        assert isinstance(response3, str)

        # End conversation
        response4 = chatbot.get_response("goodbye")
        assert chatbot.context.previous_topic == "farewells"

        # Check conversation log
        log = chatbot.get_conversation_log()
        assert len(log) == 4
        assert log[0]["category"] == "greetings"
        assert log[1]["category"] == "name_extraction"
        assert log[3]["category"] == "farewells"

    def test_sentiment_tracking_through_conversation(self):
        """Test sentiment tracking throughout a conversation."""
        chatbot = RuleBasedChatbot()

        # Send positive message
        chatbot.get_response("I feel great and awesome today")
        assert chatbot.context.sentiment_score > 0

        # Send negative message
        chatbot.get_response("This is terrible and awful")
        assert chatbot.context.sentiment_score < 0

        # Check sentiment in log
        log = chatbot.get_conversation_log()
        assert log[0]["sentiment_score"] > 0
        assert log[1]["sentiment_score"] < 0


if __name__ == "__main__":
    pytest.main([__file__])

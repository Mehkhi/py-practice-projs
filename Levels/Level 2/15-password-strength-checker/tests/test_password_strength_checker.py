"""Unit tests for password strength checker."""

import pytest
from unittest.mock import patch, MagicMock

from password_strength_checker.core import (
    calculate_length_score,
    calculate_diversity_score,
    is_common_password,
    calculate_pattern_penalty,
    calculate_entropy,
    generate_feedback,
    generate_password_suggestion,
    evaluate_password
)
from password_strength_checker.utils import normalize_password, validate_password_input


class TestLengthScoring:
    """Test length-based scoring."""

    def test_short_password(self):
        assert calculate_length_score("short") == 0

    def test_medium_password(self):
        assert calculate_length_score("mediumpass") == 15

    def test_long_password(self):
        assert calculate_length_score("verylongpassword") == 30

    def test_very_long_password(self):
        assert calculate_length_score("extremelylongpasswordhere") == 40


class TestDiversityScoring:
    """Test character diversity scoring."""

    def test_no_diversity(self):
        assert calculate_diversity_score("password") == 7  # only lowercase

    def test_lowercase_only(self):
        assert calculate_diversity_score("password") == 7

    def test_mixed_case(self):
        assert calculate_diversity_score("Password") == 14

    def test_with_digits(self):
        assert calculate_diversity_score("Password123") == 21

    def test_full_diversity(self):
        assert calculate_diversity_score("Password123!") == 35


class TestCommonPasswords:
    """Test common password detection."""

    def test_common_password(self):
        assert is_common_password("password") is True
        assert is_common_password("123456") is True

    def test_uncommon_password(self):
        assert is_common_password("MyUniquePass123!") is False

    def test_case_insensitive(self):
        assert is_common_password("PASSWORD") is True
        assert is_common_password("Password") is True


class TestPatternDetection:
    """Test pattern penalty calculation."""

    def test_no_patterns(self):
        assert calculate_pattern_penalty("MySecurePass!@#") == 0

    def test_sequential_letters(self):
        assert calculate_pattern_penalty("passwordabc") == 5

    def test_sequential_numbers(self):
        assert calculate_pattern_penalty("pass1234word") == 5

    def test_repeated_characters(self):
        assert calculate_pattern_penalty("passswordddd") == 10

    def test_multiple_patterns(self):
        assert calculate_pattern_penalty("abcd1234aaa") == 20  # capped at 20


class TestEntropyCalculation:
    """Test entropy calculations."""

    def test_empty_password(self):
        assert calculate_entropy("") == 0.0

    def test_lowercase_only(self):
        entropy = calculate_entropy("password")
        assert entropy > 0

    def test_full_diversity(self):
        entropy = calculate_entropy("MySecurePass123!")
        assert entropy > 35  # Should be high


class TestFeedbackGeneration:
    """Test feedback generation."""

    def test_weak_password_feedback(self):
        result = evaluate_password("pass")
        feedback = result["feedback"]
        assert any("too short" in f.lower() for f in feedback)
        assert any("uppercase letters" in f for f in feedback)

    def test_strong_password_feedback(self):
        result = evaluate_password("V3ryStr0ng!P@ssw0rd#2024")
        feedback = result["feedback"]
        assert any("good password" in f.lower() for f in feedback)

    def test_common_password_feedback(self):
        result = evaluate_password("password")
        feedback = result["feedback"]
        assert any("commonly used" in f.lower() for f in feedback)


class TestPasswordEvaluation:
    """Test overall password evaluation."""

    def test_empty_password(self):
        result = evaluate_password("")
        assert result["score"] == 0
        assert result["strength"] == "Very Weak"

    def test_very_weak_password(self):
        result = evaluate_password("pass")
        assert result["score"] < 20
        assert result["strength"] == "Very Weak"

    def test_weak_password(self):
        result = evaluate_password("password")
        assert result["score"] == 0  # Common password penalty
        assert result["strength"] == "Very Weak"

    def test_moderate_password(self):
        result = evaluate_password("MySecure123")
        assert 20 <= result["score"] < 40
        assert result["strength"] == "Weak"

    def test_strong_password(self):
        result = evaluate_password("MySecurePass123!")
        assert 60 <= result["score"] < 80
        assert result["strength"] == "Strong"

    def test_very_strong_password(self):
        result = evaluate_password("V3ryStr0ng!P@ssw0rd#2024")
        assert 60 <= result["score"] < 80
        assert result["strength"] == "Strong"


class TestHIBPIntegration:
    """Test Have I Been Pwned API integration."""

    @patch('password_strength_checker.core.requests.get')
    def test_hibp_found(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "DEF456:42\nABC123:1"
        mock_get.return_value = mock_response

        # Mock hashlib.sha1 to return a hash starting with ABC12
        with patch('hashlib.sha1') as mock_sha1:
            mock_hash = MagicMock()
            mock_hash.hexdigest.return_value = "ABC12DEF456"
            mock_sha1.return_value = mock_hash

            from password_strength_checker.core import check_haveibeenpwned
            result = check_haveibeenpwned("testpass")
            assert result == 42

    @patch('password_strength_checker.core.requests.get')
    def test_hibp_not_found(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "ABC123:42\nDEF456:1"
        mock_get.return_value = mock_response

        with patch('password_strength_checker.core.hashlib.sha1') as mock_sha1:
            mock_hash = MagicMock()
            mock_hash.hexdigest.return_value = "XYZ789NOTFOUND"
            mock_sha1.return_value = mock_hash

            from password_strength_checker.core import check_haveibeenpwned
            result = check_haveibeenpwned("testpass")
            assert result == 0

    @patch('password_strength_checker.core.requests.get')
    def test_hibp_error(self, mock_get):
        mock_get.side_effect = Exception("Network error")

        from password_strength_checker.core import check_haveibeenpwned
        result = check_haveibeenpwned("testpass")
        assert result is None


class TestPasswordGeneration:
    """Test password generation."""

    def test_generate_basic(self):
        password = generate_password_suggestion(8)
        assert len(password) == 8
        assert any(c.islower() for c in password)
        assert any(c.isupper() for c in password)
        assert any(c.isdigit() for c in password)
        assert any(not c.isalnum() for c in password)

    def test_generate_longer(self):
        password = generate_password_suggestion(16)
        assert len(password) == 16

    def test_generate_minimum_length(self):
        password = generate_password_suggestion(4)  # Below minimum
        assert len(password) == 8  # Should be minimum 8

    @patch("password_strength_checker.core.secrets.choice")
    def test_generate_uses_secure_random(self, mock_choice):
        mock_choice.side_effect = lambda pool: pool[0]

        password = generate_password_suggestion(12)

        assert len(password) == 12
        assert mock_choice.call_count >= 12
        assert any(c.islower() for c in password)
        assert any(c.isupper() for c in password)
        assert any(c.isdigit() for c in password)
        assert any(not c.isalnum() for c in password)


class TestUtils:
    """Test utility functions."""

    def test_normalize_password(self):
        assert normalize_password("  password  ") == "password"
        assert normalize_password("password") == "password"

    def test_validate_password_input(self):
        # Valid password
        assert validate_password_input("validpass") == []

        # Empty password
        errors = validate_password_input("")
        assert "cannot be empty" in errors[0].lower()

        # Too long
        long_pass = "a" * 200
        errors = validate_password_input(long_pass)
        assert "too long" in errors[0].lower()

        # Control characters
        errors = validate_password_input("pass\x00word")
        assert "invalid control characters" in errors[0].lower()

"""Core password strength checking functionality."""

import hashlib
import logging
import math
import re
import string
from typing import Dict, List, Optional, Tuple

import requests
import secrets

# Common passwords list (small subset for demo)
COMMON_PASSWORDS = {
    "password", "123456", "123456789", "qwerty", "abc123", "password123",
    "admin", "letmein", "welcome", "monkey", "1234567890", "iloveyou",
    "princess", "rockyou", "1234567", "12345678", "password1", "123123",
    "football", "baseball", "welcome1", "admin123", "qwerty123"
}

logger = logging.getLogger(__name__)


def calculate_length_score(password: str) -> int:
    """Calculate score based on password length.

    Args:
        password: The password to evaluate

    Returns:
        Score from 0-40 based on length
    """
    length = len(password)
    if length < 8:
        return 0
    elif length < 12:
        return 15
    elif length < 16:
        return 25
    elif length < 20:
        return 30
    else:
        return 40


def calculate_diversity_score(password: str) -> int:
    """Calculate score based on character diversity.

    Args:
        password: The password to evaluate

    Returns:
        Score from 0-35 based on character types present
    """
    score = 0
    if re.search(r'[a-z]', password):
        score += 7
    if re.search(r'[A-Z]', password):
        score += 7
    if re.search(r'\d', password):
        score += 7
    if re.search(r'[^a-zA-Z\d]', password):
        score += 14  # Special characters worth more
    return score


def is_common_password(password: str) -> bool:
    """Check if password is in common passwords list.

    Args:
        password: The password to check

    Returns:
        True if password is common, False otherwise
    """
    return password.lower() in COMMON_PASSWORDS


def calculate_pattern_penalty(password: str) -> int:
    """Calculate penalty for weak patterns.

    Args:
        password: The password to evaluate

    Returns:
        Penalty points (0-20) for detected patterns
    """
    penalty = 0

    # Check for sequential characters (abc, 123, etc.)
    if re.search(r'(?:abc|bcd|cde|def|efg|fgh|ghi|hij|ijk|jkl|klm|lmn|mno|nop|opq|pqr|qrs|rst|stu|tuv|uvw|vwx|wxy|xyz)', password.lower()):
        penalty += 5
    if re.search(r'(?:0123|1234|2345|3456|4567|5678|6789|7890|8901|9012)', password):
        penalty += 5

    # Check for repeated characters (aaa, 111, etc.)
    if re.search(r'(.)\1{2,}', password):
        penalty += 10

    return min(penalty, 20)  # Cap at 20


def calculate_entropy(password: str) -> float:
    """Calculate password entropy in bits.

    Args:
        password: The password to evaluate

    Returns:
        Entropy value in bits
    """
    if not password:
        return 0.0

    # Determine character set size
    charset_size = 0
    if re.search(r'[a-z]', password):
        charset_size += 26
    if re.search(r'[A-Z]', password):
        charset_size += 26
    if re.search(r'\d', password):
        charset_size += 10
    if re.search(r'[^a-zA-Z\d]', password):
        charset_size += 32  # Approximate special chars

    if charset_size == 0:
        return 0.0

    return len(password) * math.log2(charset_size)


def check_haveibeenpwned(password: str) -> Optional[int]:
    """Check password against Have I Been Pwned API.

    Args:
        password: The password to check

    Returns:
        Number of times password was found in breaches, or None if error
    """
    try:
        # Create SHA-1 hash of password
        sha1 = hashlib.sha1(password.encode('utf-8')).hexdigest().upper()

        # Send first 5 chars to API
        prefix = sha1[:5]
        suffix = sha1[5:]

        url = f"https://api.pwnedpasswords.com/range/{prefix}"
        response = requests.get(url, timeout=5)

        if response.status_code == 200:
            # Look for our hash suffix in the response
            lines = response.text.split('\n')
            for line in lines:
                if line.startswith(suffix):
                    count = int(line.split(':')[1])
                    logger.info(f"Password found in {count} breaches")
                    return count

        return 0  # Not found

    except Exception as e:
        logger.error(f"Error checking Have I Been Pwned API: {e}")
        return None


def generate_feedback(password: str, score: int, hibp_count: Optional[int] = None) -> List[str]:
    """Generate improvement suggestions for the password.

    Args:
        password: The password being evaluated
        score: Current strength score
        hibp_count: Number of breaches from HIBP API

    Returns:
        List of feedback strings
    """
    feedback = []

    if len(password) < 8:
        feedback.append("Password is too short. Use at least 8 characters.")
    elif len(password) < 12:
        feedback.append("Consider using 12 or more characters for better security.")

    char_types = 0
    if not re.search(r'[a-z]', password):
        feedback.append("Add lowercase letters (a-z).")
    else:
        char_types += 1

    if not re.search(r'[A-Z]', password):
        feedback.append("Add uppercase letters (A-Z).")
    else:
        char_types += 1

    if not re.search(r'\d', password):
        feedback.append("Add numbers (0-9).")
    else:
        char_types += 1

    if not re.search(r'[^a-zA-Z\d]', password):
        feedback.append("Add special characters (!@#$%^&*).")
    else:
        char_types += 1

    if char_types < 3:
        feedback.append("Use at least 3 different character types.")

    if is_common_password(password):
        feedback.append("This is a commonly used password. Choose something unique.")

    if calculate_pattern_penalty(password) > 0:
        feedback.append("Avoid sequential characters (abc, 123) or repeated characters (aaa).")

    if hibp_count and hibp_count > 0:
        feedback.append(f"This password has been found in {hibp_count} data breaches. Change it immediately!")

    if score >= 80:
        feedback.append("Great password strength!")
    elif score >= 60:
        feedback.append("Good password, but could be stronger.")
    elif score >= 40:
        feedback.append("Password is weak. Consider improvements above.")
    else:
        feedback.append("Password is very weak. Major improvements needed.")

    return feedback


def generate_password_suggestion(length: int = 12) -> str:
    """Generate a strong password suggestion.

    Args:
        length: Desired password length (minimum 8)

    Returns:
        Generated password string
    """
    length = max(length, 8)

    # Ensure at least one of each type
    password_chars = [
        string.ascii_lowercase,
        string.ascii_uppercase,
        string.digits,
        "!@#$%^&*"
    ]

    password = []

    # Start by ensuring each category is represented at least once
    for charset in password_chars:
        password.append(secrets.choice(charset))

    # Fill remaining length with random chars from all types
    all_chars = string.ascii_letters + string.digits + "!@#$%^&*"
    while len(password) < length:
        password.append(secrets.choice(all_chars))

    # Perform an in-place Fisher-Yates shuffle using secure randomness
    for i in range(len(password) - 1, 0, -1):
        j = secrets.randbelow(i + 1)
        password[i], password[j] = password[j], password[i]

    return ''.join(password)


def evaluate_password(password: str, check_hibp: bool = True) -> Dict:
    """Evaluate overall password strength.

    Args:
        password: The password to evaluate
        check_hibp: Whether to check Have I Been Pwned API

    Returns:
        Dictionary with score, strength, and feedback
    """
    if not password:
        return {
            "score": 0,
            "strength": "Very Weak",
            "length_score": 0,
            "diversity_score": 0,
            "pattern_penalty": 0,
            "entropy": 0.0,
            "is_common": False,
            "hibp_count": None,
            "feedback": ["Password cannot be empty."]
        }

    # Calculate individual scores
    length_score = calculate_length_score(password)
    diversity_score = calculate_diversity_score(password)
    pattern_penalty = calculate_pattern_penalty(password)
    entropy = calculate_entropy(password)
    is_common = is_common_password(password)

    # Base score from length and diversity
    base_score = length_score + diversity_score

    # Apply penalties
    if is_common:
        base_score = max(0, base_score - 30)
    base_score = max(0, base_score - pattern_penalty)

    # Cap at 100
    score = min(100, base_score)

    # Determine strength level
    if score >= 80:
        strength = "Very Strong"
    elif score >= 60:
        strength = "Strong"
    elif score >= 40:
        strength = "Moderate"
    elif score >= 20:
        strength = "Weak"
    else:
        strength = "Very Weak"

    # Check HIBP if requested
    hibp_count = None
    if check_hibp:
        hibp_count = check_haveibeenpwned(password)

    # Generate feedback
    feedback = generate_feedback(password, score, hibp_count)

    return {
        "score": score,
        "strength": strength,
        "length_score": length_score,
        "diversity_score": diversity_score,
        "pattern_penalty": pattern_penalty,
        "entropy": round(entropy, 2),
        "is_common": is_common,
        "hibp_count": hibp_count,
        "feedback": feedback
    }

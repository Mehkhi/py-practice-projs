"""Main entry point for the password strength checker CLI."""

import argparse
import logging
import sys
from typing import NoReturn

from .core import evaluate_password, generate_password_suggestion


def setup_logging(verbose: bool) -> None:
    """Setup logging configuration.

    Args:
        verbose: Whether to enable verbose logging
    """
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )


def print_results(result: dict, show_details: bool = False) -> None:
    """Print password evaluation results.

    Args:
        result: Evaluation result dictionary
        show_details: Whether to show detailed scoring breakdown
    """
    print(f"\nPassword Strength: {result['strength']} ({result['score']}/100)")

    if show_details:
        print("\nDetailed Scores:")
        print(f"  Length: {result['length_score']}/40")
        print(f"  Diversity: {result['diversity_score']}/35")
        print(f"  Pattern Penalty: -{result['pattern_penalty']}")
        print(f"  Entropy: {result['entropy']} bits")

    if result['is_common']:
        print("\n⚠️  WARNING: This is a commonly used password!")

    if result['hibp_count'] is not None:
        if result['hibp_count'] > 0:
            print(f"\n🚨 CRITICAL: Found in {result['hibp_count']} data breaches!")
        else:
            print("\n✅ Not found in known data breaches.")

    print("\nFeedback:")
    for feedback in result['feedback']:
        print(f"  • {feedback}")


def main() -> NoReturn:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Check password strength and get improvement suggestions",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m password_strength_checker "mypassword123"
  python -m password_strength_checker --generate
  python -m password_strength_checker --details "MySecurePass123!"
  python -m password_strength_checker --no-hibp-check "password"
        """
    )

    parser.add_argument(
        'password',
        nargs='?',
        help='Password to evaluate (if not provided, will prompt securely)'
    )

    parser.add_argument(
        '-g', '--generate',
        action='store_true',
        help='Generate a strong password suggestion'
    )

    parser.add_argument(
        '-l', '--length',
        type=int,
        default=12,
        help='Length for generated password (default: 12, minimum: 8)'
    )

    parser.add_argument(
        '-d', '--details',
        action='store_true',
        help='Show detailed scoring breakdown'
    )

    parser.add_argument(
        '--no-hibp-check',
        action='store_true',
        help='Skip Have I Been Pwned API check'
    )

    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )

    args = parser.parse_args()

    # Setup logging
    setup_logging(args.verbose)

    try:
        if args.generate:
            # Generate password suggestion
            length = max(args.length, 8)
            password = generate_password_suggestion(length)
            print(f"Generated strong password ({length} characters):")
            print(f"  {password}")
            print("\nKeep this password safe and don't share it!")
            sys.exit(0)

        # Get password to evaluate
        if args.password:
            password = args.password
        else:
            import getpass
            password = getpass.getpass("Enter password to check: ")

        if not password:
            print("Error: Password cannot be empty")
            sys.exit(1)

        # Evaluate password
        print(f"Evaluating password: {'*' * len(password)}")
        result = evaluate_password(password, check_hibp=not args.no_hibp_check)

        # Print results
        print_results(result, args.details)

        # Exit with code based on strength
        if result['score'] >= 60:
            sys.exit(0)  # Good password
        elif result['score'] >= 40:
            sys.exit(1)  # Moderate
        else:
            sys.exit(2)  # Weak

    except KeyboardInterrupt:
        print("\nOperation cancelled.")
        sys.exit(130)
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Unexpected error: {e}")
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()

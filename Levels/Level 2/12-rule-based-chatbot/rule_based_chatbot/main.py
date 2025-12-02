"""Main entry point for the rule-based chatbot CLI application."""

import argparse
import logging
import sys
from typing import Optional
from .core import RuleBasedChatbot


def setup_logging(verbose: bool = False) -> None:
    """Setup logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('chatbot.log', encoding='utf-8')
        ]
    )


def interactive_mode(chatbot: RuleBasedChatbot) -> None:
    """Run the chatbot in interactive mode."""
    print("🤖 Rule-Based Chatbot")
    print("Type 'quit', 'exit', or 'bye' to end the conversation.")
    print("Type 'help' to see what I can do!")
    print("-" * 50)

    while True:
        try:
            user_input = input("You: ").strip()

            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("Chatbot: Goodbye! Have a great day! 👋")
                break

            if not user_input:
                continue

            response = chatbot.get_response(user_input)
            print(f"Chatbot: {response}")

        except KeyboardInterrupt:
            print("\nChatbot: Goodbye! Thanks for chatting! 👋")
            break
        except EOFError:
            print("\nChatbot: Goodbye! Thanks for chatting! 👋")
            break
        except Exception as e:
            logging.error(f"Error in interactive mode: {e}")
            print("Chatbot: Sorry, something went wrong. Let's try again!")


def single_message_mode(chatbot: RuleBasedChatbot, message: str) -> None:
    """Process a single message and print the response."""
    try:
        response = chatbot.get_response(message)
        print(response)
    except Exception as e:
        logging.error(f"Error processing message: {e}")
        print("Error: Failed to process message.")


def show_stats(chatbot: RuleBasedChatbot) -> None:
    """Display conversation statistics."""
    context = chatbot.get_context()
    log = chatbot.get_conversation_log()

    print("\n📊 Conversation Statistics")
    print("=" * 30)
    print(f"Messages exchanged: {context['message_count']}")
    print(f"User name: {context['user_name'] or 'Not provided'}")
    print(f"Previous topic: {context['previous_topic'] or 'None'}")
    print(f"Average sentiment: {context['sentiment_score']:.2f}")
    print(f"Session duration: {context['session_duration']}")

    if log:
        print(f"\n📝 Recent messages:")
        for entry in log[-5:]:  # Show last 5 messages
            print(f"  • {entry['category']}: {entry['user_input'][:50]}...")


def main() -> None:
    """Main entry point for the CLI application."""
    parser = argparse.ArgumentParser(
        description="Rule-Based Chatbot - A conversational AI with pattern matching",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                           # Start interactive mode
  %(prog)s -m "Hello, how are you?"   # Single message mode
  %(prog)s --config rules.json        # Use custom rules
  %(prog)s --stats                    # Show conversation stats
  %(prog)s -v                         # Enable verbose logging
        """
    )

    parser.add_argument(
        '-m', '--message',
        type=str,
        help='Process a single message and exit'
    )

    parser.add_argument(
        '--config',
        type=str,
        help='Path to custom rules configuration file (JSON format)'
    )

    parser.add_argument(
        '--stats',
        action='store_true',
        help='Show conversation statistics and exit'
    )

    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )

    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s 1.0.0'
    )

    args = parser.parse_args()

    # Setup logging
    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)

    try:
        # Initialize chatbot
        chatbot = RuleBasedChatbot(config_file=args.config)
        logger.info("Chatbot initialized successfully")

        if args.stats:
            # For stats mode, we need some conversation data
            # Load from previous session if available
            show_stats(chatbot)
            return

        if args.message:
            # Single message mode
            single_message_mode(chatbot, args.message)
        else:
            # Interactive mode
            interactive_mode(chatbot)

    except FileNotFoundError as e:
        logger.error(f"Configuration file not found: {e}")
        print(f"Error: Configuration file '{args.config}' not found.")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Application error: {e}")
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()

#!/usr/bin/env python3

import re
import sys


def load_template(filename):
    """Load a mad libs template from a text file."""
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        print(f"Error: Template file '{filename}' not found.")
        return None
    except Exception as e:
        print(f"Error reading template file: {e}")
        return None


def find_placeholders(template):
    """Find all placeholders in the template using regex."""
    pattern = r'\{([^}]+)\}'
    return list(dict.fromkeys(re.findall(pattern, template)))


def get_user_input(placeholders):
    """Get user input for each placeholder."""
    user_words = {}

    print("\n=== Mad Libs Generator ===")
    print("Please provide the following words:\n")

    for placeholder in placeholders:
        while True:
            user_input = input(f"Enter a {placeholder}: ").strip()
            if user_input:
                user_words[placeholder] = user_input
                break
            else:
                print("Please enter a word.")

    return user_words


def fill_template(template, user_words):
    """Replace placeholders with user-provided words."""
    result = template
    for placeholder, word in user_words.items():
        pattern = r'\{' + re.escape(placeholder) + r'\}'
        result = re.sub(pattern, word, result)
    return result


def save_story(story, filename="completed_story.txt"):
    """Save the completed story to a file."""
    try:
        with open(filename, 'w', encoding='utf-8') as file:
            file.write(story)
        print(f"\nStory saved to '{filename}'")
    except Exception as e:
        print(f"Error saving story: {e}")


def main():
    """Main function to run the mad libs generator."""
    template_file = "template.txt"

    if len(sys.argv) > 1:
        template_file = sys.argv[1]

    template = load_template(template_file)
    if not template:
        return

    placeholders = find_placeholders(template)
    if not placeholders:
        print("No placeholders found in the template.")
        return

    user_words = get_user_input(placeholders)
    completed_story = fill_template(template, user_words)

    print("\n" + "="*50)
    print("YOUR COMPLETED MAD LIBS STORY:")
    print("="*50)
    print(completed_story)
    print("="*50)

    save_choice = input("\nWould you like to save this story? (y/n): ").strip().lower()
    if save_choice in ['y', 'yes']:
        save_story(completed_story)


if __name__ == "__main__":
    main()

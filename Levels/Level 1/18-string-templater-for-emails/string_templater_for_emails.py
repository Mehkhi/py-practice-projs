#!/usr/bin/env python3
"""
String Templater for Emails

A command-line program that loads email templates and replaces variables
with provided data to generate personalized emails.
"""

import json
import re
import os
from typing import Dict, List, Any, Optional


class EmailTemplater:
    """Main class for email templating functionality."""

    def __init__(self):
        self.template = ""
        self.variables = {}

    def load_template(self, template_source: str) -> bool:
        """
        Load email template from file or use provided string.

        Args:
            template_source: File path or template string

        Returns:
            bool: True if template loaded successfully, False otherwise
        """
        try:
            if os.path.isfile(template_source):
                with open(template_source, 'r', encoding='utf-8') as file:
                    self.template = file.read()
                return True
            else:
                # Check if it's clearly a file path (contains path separators or ends with common extensions)
                if ('/' in template_source or '\\' in template_source) or \
                   template_source.endswith(('.txt', '.html', '.md', '.template')):
                    print(f"Error loading template: File '{template_source}' not found")
                    return False
                else:
                    # Treat as template string
                    self.template = template_source
                    return True
        except Exception as e:
            print(f"Error loading template: {e}")
            return False

    def detect_variables(self) -> List[str]:
        """
        Detect all template variables in the format {{variable_name}}.

        Returns:
            List of variable names found in the template
        """
        pattern = r'\{\{([^}]+)\}\}'
        variables = re.findall(pattern, self.template)
        return list(set(variables))  # Remove duplicates

    def replace_variables(self, data: Dict[str, Any]) -> str:
        """
        Replace template variables with provided data.

        Args:
            data: Dictionary containing variable values

        Returns:
            str: Template with variables replaced
        """
        result = self.template

        # Replace simple variables
        for key, value in data.items():
            placeholder = f"{{{{{key}}}}}"
            result = result.replace(placeholder, str(value))

        # Handle conditional sections
        result = self._process_conditionals(result, data)

        return result

    def _process_conditionals(self, text: str, data: Dict[str, Any]) -> str:
        """
        Process conditional sections in the template.

        Format: {{if variable}}...{{else}}...{{endif}}

        Args:
            text: Template text with conditionals
            data: Data dictionary

        Returns:
            str: Text with conditionals processed
        """
        # Pattern to match conditional blocks
        pattern = r'\{\{if\s+([^}]+)\}\}(.*?)(?:\{\{else\}\}(.*?))?\{\{endif\}\}'

        def replace_conditional(match):
            condition_var = match.group(1).strip()
            if_block = match.group(2)
            else_block = match.group(3) if match.group(3) else ""

            # Check if condition variable exists and is truthy
            if condition_var in data and data[condition_var]:
                return if_block
            else:
                return else_block

        return re.sub(pattern, replace_conditional, text, flags=re.DOTALL)

    def load_data_from_json(self, json_file: str) -> Optional[Dict[str, Any]]:
        """
        Load data from a JSON file.

        Args:
            json_file: Path to JSON file

        Returns:
            Dict containing data or None if error
        """
        try:
            with open(json_file, 'r', encoding='utf-8') as file:
                return json.load(file)
        except Exception as e:
            print(f"Error loading JSON file: {e}")
            return None

    def generate_batch_emails(self, data_list: List[Dict[str, Any]]) -> List[str]:
        """
        Generate multiple emails from a list of data dictionaries.

        Args:
            data_list: List of data dictionaries

        Returns:
            List of generated email strings
        """
        emails = []
        for data in data_list:
            email = self.replace_variables(data)
            emails.append(email)
        return emails


def get_user_input(prompt: str, required: bool = True) -> str:
    """
    Get user input with validation.

    Args:
        prompt: Input prompt message
        required: Whether input is required

    Returns:
        str: User input
    """
    while True:
        user_input = input(prompt).strip()
        if user_input or not required:
            return user_input
        print("This field is required. Please try again.")


def interactive_mode():
    """Run the program in interactive mode."""
    print("=== Email String Templater ===")
    print("This program helps you create personalized emails from templates.")
    print()

    templater = EmailTemplater()

    # Get template
    print("1. Template Input:")
    print("   a) Load from file")
    print("   b) Enter template manually")

    template_choice = get_user_input("Choose option (a/b): ").lower()

    if template_choice == 'a':
        template_file = get_user_input("Enter template file path: ")
        if not templater.load_template(template_file):
            return
    else:
        print("\nEnter your email template (use {{variable_name}} for variables):")
        print("Example: Hello {{name}}, your order {{order_id}} is ready!")
        print("Press Ctrl+D (Unix) or Ctrl+Z (Windows) when finished:")
        try:
            template_lines = []
            while True:
                line = input()
                template_lines.append(line)
        except EOFError:
            template = '\n'.join(template_lines)
            templater.load_template(template)

    # Detect variables
    variables = templater.detect_variables()
    if not variables:
        print("No variables found in template.")
        return

    print(f"\nDetected variables: {', '.join(variables)}")

    # Get data input method
    print("\n2. Data Input:")
    print("   a) Load from JSON file")
    print("   b) Enter data manually")
    print("   c) Batch mode (multiple emails)")

    data_choice = get_user_input("Choose option (a/b/c): ").lower()

    if data_choice == 'a':
        json_file = get_user_input("Enter JSON file path: ")
        data = templater.load_data_from_json(json_file)
        if data is None:
            return

        if isinstance(data, list):
            # Batch processing
            emails = templater.generate_batch_emails(data)
            print(f"\nGenerated {len(emails)} emails:")
            for i, email in enumerate(emails, 1):
                print(f"\n--- Email {i} ---")
                print(email)
        else:
            # Single email
            email = templater.replace_variables(data)
            print("\n--- Generated Email ---")
            print(email)

    elif data_choice == 'b':
        # Manual data entry
        data = {}
        for var in variables:
            value = get_user_input(f"Enter value for '{var}': ")
            data[var] = value

        email = templater.replace_variables(data)
        print("\n--- Generated Email ---")
        print(email)

    elif data_choice == 'c':
        # Batch mode
        print("\nEnter data for each email (press Enter with empty name to finish):")
        data_list = []

        while True:
            print(f"\n--- Email {len(data_list) + 1} ---")
            email_data = {}

            for var in variables:
                value = get_user_input(f"Enter value for '{var}': ", required=False)
                email_data[var] = value

            if not any(email_data.values()):
                break

            data_list.append(email_data)

        if data_list:
            emails = templater.generate_batch_emails(data_list)
            print(f"\nGenerated {len(emails)} emails:")
            for i, email in enumerate(emails, 1):
                print(f"\n--- Email {i} ---")
                print(email)
        else:
            print("No emails generated.")


def main():
    """Main function to run the program."""
    try:
        interactive_mode()
    except KeyboardInterrupt:
        print("\n\nProgram interrupted by user.")
    except Exception as e:
        print(f"\nAn error occurred: {e}")


if __name__ == "__main__":
    main()

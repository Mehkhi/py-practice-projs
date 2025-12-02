# Mad Libs Generator

A command-line Mad Libs generator that creates funny stories by filling in templates with user-provided words.

## What It Does

This program loads a story template with placeholders, prompts the user to provide words for each placeholder, and then generates a completed story. The placeholders are identified by curly braces `{}` in the template file.

## How to Run

1. Make sure you have Python 3.7 or higher installed
2. Run the program with the default template:
   ```bash
   python mad_libs_generator.py
   ```
3. Or specify a custom template file:
   ```bash
   python mad_libs_generator.py my_template.txt
   ```

## Example Usage

```
$ python mad_libs_generator.py

=== Mad Libs Generator ===
Please provide the following words:

Enter a adjective: silly
Enter a noun: monkey
Enter a verb: danced
Enter a adverb: gracefully
...

==================================================
YOUR COMPLETED MAD LIBS STORY:
==================================================
The silly monkey danced gracefully...
==================================================

Would you like to save this story? (y/n): y
Story saved to 'completed_story.txt'
```

## Template Format

Create your own template files using the following format:
- Use `{placeholder_name}` for words that need to be filled in
- Placeholder names should be descriptive (e.g., `{adjective}`, `{noun}`, `{verb}`)
- Save templates as `.txt` files

Example template:
```
The {adjective} {noun} decided to {verb} to the {place}.
```

## Features

- Load templates from text files
- Automatic placeholder detection using regex
- User input validation
- Story completion and display
- Optional story saving to file
- Error handling for missing files

## Testing

Run the unit tests:
```bash
python -m pytest test_mad_libs_generator.py -v
```

Or run with unittest:
```bash
python test_mad_libs_generator.py
```

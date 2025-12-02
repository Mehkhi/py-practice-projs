# CLI Address Autocomplete

A command-line tool for fast address autocomplete using trigram indexing and fuzzy matching.

## Features

- Build trigram index from CSV address dataset
- Fast prefix and fuzzy matching
- Relevance-based ranking of results
- Pagination for large result sets
- Simple CLI interface

## Installation

1. Clone or download the project
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

```bash
# Basic search
python -m cli_address_autocomplete "Main St"

# With options
python -m cli_address_autocomplete "Oak Ave" --limit 5 --page 1

# Specify custom dataset
python -m cli_address_autocomplete "Elm" --dataset my_addresses.csv
```

## Dataset Format

The tool expects a CSV file with addresses in the first column:

```csv
123 Main St, Anytown, USA
456 Oak Ave, Somewhere, USA
```

## Configuration

- `--limit`: Maximum number of results (default: 10)
- `--page`: Page number for pagination (default: 1)
- `--dataset`: Path to address dataset CSV (default: sample_addresses.csv)

## Limitations

- Requires at least 3 characters in query for trigram matching
- Dataset must be in CSV format with addresses in first column
- Matching is case-insensitive but punctuation-sensitive

## Development

Run tests:
```bash
pytest tests/
```

Format code:
```bash
black cli_address_autocomplete/
ruff cli_address_autocomplete/
```

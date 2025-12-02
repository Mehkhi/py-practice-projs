# PDF Search Engine

A simple PDF search engine with inverted index, ranking, and boolean queries.

## Features

- **Text Extraction**: Extracts text from PDFs using pdfminer.
- **Tokenization**: Normalizes text with lowercasing, stopword removal, and stemming.
- **Inverted Index**: Supports phrase queries and term searches.
- **Ranking**: Uses TF-IDF with field weights for titles.
- **Boolean Queries**: Supports AND, OR, NOT operators.
- **Persistent Index**: Saves/loads compressed index.
- **Snippets**: Generates highlighted snippets.

## Usage

1. Place PDF files in `sample_pdfs/`.
2. Build the index: `python main.py build sample_pdfs`
3. Search: `python main.py search "machine learning"`

## Testing

Run tests: `python -m unittest tests.test_pdf_search`

## Requirements

- pdfminer.six
- nltk
- numpy

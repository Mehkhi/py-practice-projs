# RSS Reader

A professional command-line RSS feed reader built with Python. This tool allows you to manage multiple RSS feeds, track read/unread articles, search content, and export articles to various formats.

## Features

- **Feed Management**: Add, list, and remove RSS feeds
- **Article Reading**: Display articles with title, date, summary, and author
- **Read/Unread Tracking**: Mark articles as read and filter by read status
- **Search**: Full-text search across article titles and summaries
- **Export**: Export articles to HTML or Markdown formats
- **Database Storage**: SQLite database for persistent storage
- **Logging**: Comprehensive logging for debugging and monitoring

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Setup

1. Clone or download the project
2. Navigate to the project directory
3. Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Basic Commands

#### Add a Feed
```bash
python -m rss_reader add-feed "BBC News" "http://feeds.bbci.co.uk/news/rss.xml"
```

#### List All Feeds
```bash
python -m rss_reader list-feeds
```

#### Fetch Articles from a Feed
```bash
python -m rss_reader fetch 1
```

#### List Articles
```bash
# List all articles
python -m rss_reader list

# List articles from a specific feed
python -m rss_reader list --feed-id 1

# List only unread articles
python -m rss_reader list --unread
```

#### Mark Articles as Read
```bash
# Mark a specific article as read
python -m rss_reader mark-read --article-id 1

# Mark all articles in a feed as read
python -m rss_reader mark-read --feed-id 1
```

#### Search Articles
```bash
python -m rss_reader search "python"
```

#### Export Articles
```bash
# Export all articles to HTML
python -m rss_reader export articles.html

# Export unread articles to Markdown
python -m rss_reader export articles.md --format markdown --unread-only

# Export articles from a specific feed
python -m rss_reader export feed_articles.html --feed-id 1
```

### Advanced Options

#### Custom Database Location
```bash
python -m rss_reader --db /path/to/custom.db list
```

#### Logging Level
```bash
python -m rss_reader --log-level DEBUG list
```

## Configuration

The RSS reader uses a SQLite database (`rss_reader.db` by default) to store:
- Feed information (name, URL)
- Article data (title, link, summary, author, publication date)
- Read/unread status

Log files are saved to `rss_reader.log` in the current directory.

## Sample RSS Feeds

Here are some popular RSS feeds you can try:

```bash
# Technology
python -m rss_reader add-feed "TechCrunch" "https://techcrunch.com/feed/"
python -m rss_reader add-feed "Hacker News" "https://hnrss.org/frontpage"

# News
python -m rss_reader add-feed "BBC News" "http://feeds.bbci.co.uk/news/rss.xml"
python -m rss_reader add-feed "Reuters" "https://www.reuters.com/rssFeed/worldNews"

# Development
python -m rss_reader add-feed "Python Official Blog" "https://blog.python.org/feeds/posts/default"
```

## Examples

### Daily Workflow
```bash
# 1. Fetch latest articles from all feeds
python -m rss_reader list-feeds | while read line; do
    feed_id=$(echo $line | cut -d: -f1)
    python -m rss_reader fetch $feed_id
done

# 2. List unread articles
python -m rss_reader list --unread

# 3. Mark articles as read after reading
python -m rss_reader mark-read --article-id 123

# 4. Export interesting articles
python -m rss_reader export saved_articles.html --unread-only
```

### Search and Export
```bash
# Search for articles about Python
python -m rss_reader search "python"

# Export search results to Markdown
python -m rss_reader export python_articles.md --format markdown
```

## Testing

Run the test suite:

```bash
python -m pytest tests/ -v
```

Or run tests directly:

```bash
python -m unittest tests.test_rss_reader
```

## Development

### Project Structure
```
21-rss-reader/
├── rss_reader/          # Main package
│   ├── __init__.py      # Package initialization
│   ├── main.py          # CLI interface
│   ├── core.py          # Core RSS functionality
│   └── utils.py         # Utility functions
├── tests/               # Test suite
│   ├── __init__.py
│   └── test_rss_reader.py
├── requirements.txt     # Dependencies
├── README.md           # This file
├── CHECKLIST.md        # Feature checklist
└── SPEC.md             # Project specification
```

### Code Quality

The project follows Python best practices:
- Type hints on public functions
- Comprehensive error handling
- Logging for debugging
- Unit tests with high coverage
- PEP 8 compliant code style

### Dependencies

- `feedparser`: RSS/Atom feed parsing
- `requests`: HTTP requests (for future enhancements)
- `beautifulsoup4`: HTML parsing for summary cleaning
- `lxml`: XML parser backend

## Known Limitations

- No automatic feed refreshing (manual fetch required)
- No feed categorization or tagging
- Limited to RSS/Atom formats
- No authentication support for private feeds
- No concurrent feed fetching

## Troubleshooting

### Common Issues

1. **Feed not accessible**: Check the feed URL and network connectivity
2. **Database locked**: Ensure only one instance is running
3. **Encoding issues**: Some feeds may have non-standard encoding

### Debug Mode

Enable debug logging for troubleshooting:

```bash
python -m rss_reader --log-level DEBUG list
```

Check the log file `rss_reader.log` for detailed error information.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

This project is part of the Python Practice Projects collection and is provided for educational purposes.

## Version History

- **v1.0.0**: Initial release with core RSS reading functionality

---

**Built with ❤️ for Python learners**

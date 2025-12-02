"""Unit tests for RSS Reader."""

import unittest
import tempfile
import os
import datetime
from unittest.mock import patch, MagicMock
import sqlite3

from rss_reader.core import RSSReader, Article, Feed
from rss_reader.utils import format_article_display, export_to_html, export_to_markdown


class TestRSSReader(unittest.TestCase):
    """Test cases for RSSReader class."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False)
        self.temp_db.close()
        self.reader = RSSReader(self.temp_db.name)

    def tearDown(self):
        """Clean up test fixtures."""
        os.unlink(self.temp_db.name)

    def test_database_initialization(self):
        """Test database tables are created."""
        # Check if tables exist
        with sqlite3.connect(self.temp_db.name) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            self.assertIn("feeds", tables)
            self.assertIn("articles", tables)

    def test_add_feed(self):
        """Test adding a new feed."""
        result = self.reader.add_feed("Test Feed", "http://example.com/rss")
        self.assertTrue(result)

        # Verify feed was added
        feeds = self.reader.list_feeds()
        self.assertEqual(len(feeds), 1)
        self.assertEqual(feeds[0].name, "Test Feed")
        self.assertEqual(feeds[0].url, "http://example.com/rss")

    def test_add_duplicate_feed(self):
        """Test adding duplicate feed fails."""
        self.reader.add_feed("Test Feed", "http://example.com/rss")
        result = self.reader.add_feed("Test Feed", "http://example.com/rss")
        self.assertFalse(result)

    def test_list_feeds_empty(self):
        """Test listing feeds when none exist."""
        feeds = self.reader.list_feeds()
        self.assertEqual(len(feeds), 0)

    def test_remove_feed(self):
        """Test removing a feed."""
        # Add a feed first
        self.reader.add_feed("Test Feed", "http://example.com/rss")
        feeds = self.reader.list_feeds()
        feed_id = feeds[0].feed_id

        # Remove the feed
        result = self.reader.remove_feed(feed_id)
        self.assertTrue(result)

        # Verify feed was removed
        feeds = self.reader.list_feeds()
        self.assertEqual(len(feeds), 0)

    def test_remove_nonexistent_feed(self):
        """Test removing non-existent feed."""
        result = self.reader.remove_feed(999)
        self.assertFalse(result)

    @patch("rss_reader.core.feedparser.parse")
    def test_fetch_articles(self, mock_parse):
        """Test fetching articles from a feed."""
        # Mock feedparser response
        mock_entry = MagicMock()
        mock_entry.title = "Test Article"
        mock_entry.link = "http://example.com/article1"
        mock_entry.summary = "<p>Test summary</p>"
        mock_entry.author = "Test Author"
        mock_entry.published_parsed = (2023, 1, 1, 12, 0, 0, 0, 1, 0)

        mock_parsed = MagicMock()
        mock_parsed.entries = [mock_entry]
        mock_parsed.bozo = False
        mock_parse.return_value = mock_parsed

        # Add a feed and fetch articles
        self.reader.add_feed("Test Feed", "http://example.com/rss")
        feeds = self.reader.list_feeds()
        feed_id = feeds[0].feed_id

        articles = self.reader.fetch_articles(feed_id)
        self.assertEqual(len(articles), 1)
        self.assertEqual(articles[0].title, "Test Article")
        self.assertEqual(articles[0].link, "http://example.com/article1")
        self.assertEqual(articles[0].summary, "Test summary")

    def test_get_articles(self):
        """Test retrieving articles from database."""
        # Add a feed and manually insert an article
        self.reader.add_feed("Test Feed", "http://example.com/rss")
        feeds = self.reader.list_feeds()
        feed_id = feeds[0].feed_id

        with sqlite3.connect(self.temp_db.name) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO articles (feed_id, title, link, summary, published)
                VALUES (?, ?, ?, ?, ?)
            """,
                (
                    feed_id,
                    "Test Article",
                    "http://example.com/article1",
                    "Test summary",
                    datetime.datetime.now(),
                ),
            )
            conn.commit()

        articles = self.reader.get_articles()
        self.assertEqual(len(articles), 1)
        self.assertEqual(articles[0].title, "Test Article")

    def test_get_unread_articles(self):
        """Test retrieving only unread articles."""
        # Add a feed and manually insert articles
        self.reader.add_feed("Test Feed", "http://example.com/rss")
        feeds = self.reader.list_feeds()
        feed_id = feeds[0].feed_id

        with sqlite3.connect(self.temp_db.name) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO articles (feed_id, title, link, summary, is_read)
                VALUES (?, ?, ?, ?, ?)
            """,
                (
                    feed_id,
                    "Unread Article",
                    "http://example.com/article1",
                    "Test summary",
                    False,
                ),
            )
            cursor.execute(
                """
                INSERT INTO articles (feed_id, title, link, summary, is_read)
                VALUES (?, ?, ?, ?, ?)
            """,
                (
                    feed_id,
                    "Read Article",
                    "http://example.com/article2",
                    "Test summary",
                    True,
                ),
            )
            conn.commit()

        articles = self.reader.get_articles(unread_only=True)
        self.assertEqual(len(articles), 1)
        self.assertEqual(articles[0].title, "Unread Article")

    def test_mark_article_read(self):
        """Test marking an article as read."""
        # Add a feed and manually insert an article
        self.reader.add_feed("Test Feed", "http://example.com/rss")
        feeds = self.reader.list_feeds()
        feed_id = feeds[0].feed_id

        with sqlite3.connect(self.temp_db.name) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO articles (feed_id, title, link, summary, is_read)
                VALUES (?, ?, ?, ?, ?)
            """,
                (
                    feed_id,
                    "Test Article",
                    "http://example.com/article1",
                    "Test summary",
                    False,
                ),
            )
            conn.commit()

        articles = self.reader.get_articles()
        article_id = articles[0].article_id

        result = self.reader.mark_article_read(article_id)
        self.assertTrue(result)

        # Verify article is now read
        articles = self.reader.get_articles()
        self.assertTrue(articles[0].is_read)

    def test_mark_feed_read(self):
        """Test marking all articles in a feed as read."""
        # Add a feed and manually insert articles
        self.reader.add_feed("Test Feed", "http://example.com/rss")
        feeds = self.reader.list_feeds()
        feed_id = feeds[0].feed_id

        with sqlite3.connect(self.temp_db.name) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO articles (feed_id, title, link, summary, is_read)
                VALUES (?, ?, ?, ?, ?)
            """,
                (
                    feed_id,
                    "Article 1",
                    "http://example.com/article1",
                    "Test summary",
                    False,
                ),
            )
            cursor.execute(
                """
                INSERT INTO articles (feed_id, title, link, summary, is_read)
                VALUES (?, ?, ?, ?, ?)
            """,
                (
                    feed_id,
                    "Article 2",
                    "http://example.com/article2",
                    "Test summary",
                    False,
                ),
            )
            conn.commit()

        result = self.reader.mark_feed_read(feed_id)
        self.assertTrue(result)

        # Verify all articles are now read
        articles = self.reader.get_articles(feed_id=feed_id)
        self.assertTrue(all(article.is_read for article in articles))

    def test_mark_feed_read_missing_feed(self):
        """Marking an unknown feed should fail."""
        result = self.reader.mark_feed_read(12345)
        self.assertFalse(result)

    def test_search_articles(self):
        """Test searching articles."""
        # Add a feed and manually insert articles
        self.reader.add_feed("Test Feed", "http://example.com/rss")
        feeds = self.reader.list_feeds()
        feed_id = feeds[0].feed_id

        with sqlite3.connect(self.temp_db.name) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO articles (feed_id, title, link, summary)
                VALUES (?, ?, ?, ?)
            """,
                (
                    feed_id,
                    "Python Tutorial",
                    "http://example.com/article1",
                    "Learn Python programming",
                ),
            )
            cursor.execute(
                """
                INSERT INTO articles (feed_id, title, link, summary)
                VALUES (?, ?, ?, ?)
            """,
                (
                    feed_id,
                    "JavaScript Guide",
                    "http://example.com/article2",
                    "Learn JavaScript basics",
                ),
            )
            conn.commit()

        # Search for Python
        articles = self.reader.search_articles("Python")
        self.assertEqual(len(articles), 1)
        self.assertEqual(articles[0].title, "Python Tutorial")

        # Search for Learn (should match both)
        articles = self.reader.search_articles("Learn")
        self.assertEqual(len(articles), 2)


class TestArticle(unittest.TestCase):
    """Test cases for Article class."""

    def test_article_creation(self):
        """Test creating an article."""
        article = Article(
            title="Test Article",
            link="http://example.com/article",
            summary="Test summary",
        )
        self.assertEqual(article.title, "Test Article")
        self.assertEqual(article.link, "http://example.com/article")
        self.assertEqual(article.summary, "Test summary")
        self.assertFalse(article.is_read)


class TestFeed(unittest.TestCase):
    """Test cases for Feed class."""

    def test_feed_creation(self):
        """Test creating a feed."""
        feed = Feed(name="Test Feed", url="http://example.com/rss")
        self.assertEqual(feed.name, "Test Feed")
        self.assertEqual(feed.url, "http://example.com/rss")


class TestUtils(unittest.TestCase):
    """Test cases for utility functions."""

    def setUp(self):
        """Set up test fixtures."""
        self.article = Article(
            title="Test Article",
            link="http://example.com/article",
            summary="This is a test article summary",
            author="Test Author",
            published=datetime.datetime(2023, 1, 1, 12, 0, 0),
            is_read=False,
        )

    def test_format_article_display(self):
        """Test formatting article for display."""
        display = format_article_display(self.article)
        self.assertIn("○ Test Article", display)
        self.assertIn("http://example.com/article", display)
        self.assertIn("Test Author", display)
        self.assertIn("2023-01-01 12:00", display)
        self.assertIn("This is a test article summary", display)

    def test_format_article_display_read(self):
        """Test formatting read article for display."""
        self.article.is_read = True
        display = format_article_display(self.article)
        self.assertIn("✓ Test Article", display)

    def test_export_to_html(self):
        """Test exporting articles to HTML."""
        articles = [self.article]
        with tempfile.NamedTemporaryFile(mode="w", suffix=".html", delete=False) as f:
            filename = f.name

        try:
            result = export_to_html(articles, filename)
            self.assertTrue(result)

            # Check file was created and contains expected content
            with open(filename, "r") as f:
                content = f.read()
                self.assertIn("Test Article", content)
                self.assertIn("http://example.com/article", content)
                self.assertIn("Test Author", content)
        finally:
            os.unlink(filename)

    def test_export_to_markdown(self):
        """Test exporting articles to Markdown."""
        articles = [self.article]
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            filename = f.name

        try:
            result = export_to_markdown(articles, filename)
            self.assertTrue(result)

            # Check file was created and contains expected content
            with open(filename, "r") as f:
                content = f.read()
                self.assertIn("# RSS Articles Export", content)
                self.assertIn("○ Test Article", content)
                self.assertIn("http://example.com/article", content)
                self.assertIn("Test Author", content)
        finally:
            os.unlink(filename)


if __name__ == "__main__":
    unittest.main()

"""Core RSS feed parsing and management functionality."""

import datetime
import logging
import sqlite3
from dataclasses import dataclass
from html.parser import HTMLParser
from typing import List, Optional

try:  # pragma: no cover - executed when dependency is available
    import feedparser  # type: ignore
except ModuleNotFoundError:  # pragma: no cover - exercised via dedicated tests
    from email.utils import parsedate_to_datetime
    from types import SimpleNamespace
    from urllib.request import urlopen
    from urllib.error import URLError
    import xml.etree.ElementTree as ET

    def _fallback_parse(url: str):
        """Simple RSS parser used when feedparser is unavailable."""
        try:
            if url.startswith(("http://", "https://")):
                with urlopen(url) as response:
                    data = response.read()
            else:
                with open(url, "rb") as file_obj:
                    data = file_obj.read()
        except (URLError, OSError) as exc:
            return SimpleNamespace(entries=[], bozo=True, bozo_exception=exc)

        try:
            root = ET.fromstring(data)
        except ET.ParseError as exc:
            return SimpleNamespace(entries=[], bozo=True, bozo_exception=exc)

        entries = []
        for item in root.findall(".//item"):
            title = item.findtext("title") or "No Title"
            link = item.findtext("link") or ""
            summary = item.findtext("description") or ""
            author = item.findtext("author")
            published = None
            published_parsed = None
            raw_date = item.findtext("pubDate")
            if raw_date:
                try:
                    parsed = parsedate_to_datetime(raw_date)
                    if parsed is not None:
                        if parsed.tzinfo:
                            parsed = parsed.astimezone(datetime.timezone.utc)
                        published = parsed.replace(tzinfo=None)
                        published_parsed = published.timetuple()
                except (TypeError, ValueError):
                    pass

            entries.append(
                SimpleNamespace(
                    title=title,
                    link=link,
                    summary=summary,
                    author=author,
                    published=published,
                    published_parsed=published_parsed,
                )
            )

        return SimpleNamespace(entries=entries, bozo=False, bozo_exception=None)

    feedparser = SimpleNamespace(parse=_fallback_parse)


class _HTMLStripper(HTMLParser):
    """Remove markup when BeautifulSoup is unavailable."""

    def __init__(self) -> None:
        super().__init__()
        self._chunks: List[str] = []

    def handle_data(self, data: str) -> None:
        self._chunks.append(data)

    def get_text(self) -> str:
        return "".join(self._chunks)


def _clean_summary(summary: str) -> str:
    """Strip HTML and limit length for article summaries."""
    stripper = _HTMLStripper()
    stripper.feed(summary)
    stripper.close()
    text = stripper.get_text().strip()
    return text[:500]


@dataclass
class Article:
    """Represents an RSS article."""

    title: str
    link: str
    summary: str
    published: Optional[datetime.datetime] = None
    author: Optional[str] = None
    feed_id: Optional[int] = None
    article_id: Optional[int] = None
    is_read: bool = False


@dataclass
class Feed:
    """Represents an RSS feed."""

    name: str
    url: str
    feed_id: Optional[int] = None


class RSSReader:
    """Main RSS reader class for managing feeds and articles."""

    def __init__(self, db_path: str = "rss_reader.db"):
        """Initialize RSS reader with database."""
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        self._init_database()

    def _init_database(self) -> None:
        """Initialize database tables."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Create feeds table
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS feeds (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL UNIQUE,
                        url TEXT NOT NULL UNIQUE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """
                )

                # Create articles table
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS articles (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        feed_id INTEGER NOT NULL,
                        title TEXT NOT NULL,
                        link TEXT NOT NULL UNIQUE,
                        summary TEXT,
                        author TEXT,
                        published TIMESTAMP,
                        is_read BOOLEAN DEFAULT FALSE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (feed_id) REFERENCES feeds (id)
                    )
                """
                )

                conn.commit()
                self.logger.info("Database initialized successfully")
        except sqlite3.Error as e:
            self.logger.error(f"Database initialization failed: {e}")
            raise

    def add_feed(self, name: str, url: str) -> bool:
        """Add a new RSS feed."""
        try:
            # Test if feed is accessible
            parsed = feedparser.parse(url)
            if parsed.bozo and parsed.bozo_exception:
                self.logger.warning(f"Feed may have issues: {parsed.bozo_exception}")

            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO feeds (name, url) VALUES (?, ?)", (name, url)
                )
                conn.commit()
                self.logger.info(f"Added feed: {name}")
                return True
        except sqlite3.IntegrityError:
            self.logger.error(f"Feed with name '{name}' or URL '{url}' already exists")
            return False
        except Exception as e:
            self.logger.error(f"Failed to add feed: {e}")
            return False

    def list_feeds(self) -> List[Feed]:
        """List all registered feeds."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id, name, url FROM feeds ORDER BY name")
                rows = cursor.fetchall()
                return [Feed(row[1], row[2], row[0]) for row in rows]
        except sqlite3.Error as e:
            self.logger.error(f"Failed to list feeds: {e}")
            return []

    def remove_feed(self, feed_id: int) -> bool:
        """Remove a feed and its articles."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                # Check if feed exists
                cursor.execute("SELECT id FROM feeds WHERE id = ?", (feed_id,))
                if not cursor.fetchone():
                    self.logger.warning(f"Feed with ID {feed_id} not found")
                    return False

                # Delete articles first (foreign key constraint)
                cursor.execute("DELETE FROM articles WHERE feed_id = ?", (feed_id,))
                # Delete feed
                cursor.execute("DELETE FROM feeds WHERE id = ?", (feed_id,))
                conn.commit()
                self.logger.info(f"Removed feed with ID: {feed_id}")
                return True
        except sqlite3.Error as e:
            self.logger.error(f"Failed to remove feed: {e}")
            return False

    def fetch_articles(self, feed_id: int) -> List[Article]:
        """Fetch and parse articles from a specific feed."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT url FROM feeds WHERE id = ?", (feed_id,))
                result = cursor.fetchone()

                if not result:
                    self.logger.error(f"Feed with ID {feed_id} not found")
                    return []

                feed_url = result[0]
                parsed = feedparser.parse(feed_url)

                articles = []
                for entry in parsed.entries:
                    # Clean HTML from summary
                    summary = getattr(entry, "summary", "")
                    if summary:
                        summary = _clean_summary(str(summary))

                    # Parse published date
                    published = None
                    if hasattr(entry, "published_parsed") and entry.published_parsed:
                        published = datetime.datetime(*entry.published_parsed[:6])

                    article = Article(
                        title=getattr(entry, "title", "No Title"),
                        link=getattr(entry, "link", ""),
                        summary=summary,
                        published=published,
                        author=getattr(entry, "author", None),
                        feed_id=feed_id,
                    )
                    articles.append(article)

                # Save articles to database
                self._save_articles(articles)
                self.logger.info(
                    f"Fetched {len(articles)} articles from feed {feed_id}"
                )
                return articles

        except Exception as e:
            self.logger.error(f"Failed to fetch articles: {e}")
            return []

    def _save_articles(self, articles: List[Article]) -> None:
        """Save articles to database, avoiding duplicates."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                for article in articles:
                    try:
                        cursor.execute(
                            """
                            INSERT OR IGNORE INTO articles
                            (feed_id, title, link, summary, author, published)
                            VALUES (?, ?, ?, ?, ?, ?)
                        """,
                            (
                                article.feed_id,
                                article.title,
                                article.link,
                                article.summary,
                                article.author,
                                article.published,
                            ),
                        )
                    except sqlite3.Error as e:
                        self.logger.warning(
                            f"Failed to save article '{article.title}': {e}"
                        )
                conn.commit()
        except sqlite3.Error as e:
            self.logger.error(f"Failed to save articles: {e}")

    def get_articles(
        self, feed_id: Optional[int] = None, unread_only: bool = False
    ) -> List[Article]:
        """Get articles from database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                query = """
                    SELECT a.id, a.feed_id, a.title, a.link, a.summary,
                           a.author, a.published, a.is_read
                    FROM articles a
                """
                params = []

                if feed_id is not None:
                    query += " WHERE a.feed_id = ?"
                    params.append(feed_id)

                if unread_only:
                    if feed_id is not None:
                        query += " AND a.is_read = FALSE"
                    else:
                        query += " WHERE a.is_read = FALSE"

                query += " ORDER BY a.published DESC, a.created_at DESC"

                cursor.execute(query, params)
                rows = cursor.fetchall()

                articles = []
                for row in rows:
                    article = Article(
                        title=row[2],
                        link=row[3],
                        summary=row[4],
                        author=row[5],
                        published=(
                            datetime.datetime.fromisoformat(row[6]) if row[6] else None
                        ),
                        feed_id=row[1],
                        article_id=row[0],
                        is_read=bool(row[7]),
                    )
                    articles.append(article)

                return articles
        except sqlite3.Error as e:
            self.logger.error(f"Failed to get articles: {e}")
            return []

    def mark_article_read(self, article_id: int) -> bool:
        """Mark an article as read."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE articles SET is_read = TRUE WHERE id = ?", (article_id,)
                )
                conn.commit()
                return cursor.rowcount > 0
        except sqlite3.Error as e:
            self.logger.error(f"Failed to mark article as read: {e}")
            return False

    def mark_feed_read(self, feed_id: int) -> bool:
        """Mark all articles in a feed as read."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1 FROM feeds WHERE id = ?", (feed_id,))
                if cursor.fetchone() is None:
                    self.logger.warning(f"Feed with ID {feed_id} not found")
                    return False
                cursor.execute(
                    "UPDATE articles SET is_read = TRUE WHERE feed_id = ?", (feed_id,)
                )
                conn.commit()
                return True
        except sqlite3.Error as e:
            self.logger.error(f"Failed to mark feed as read: {e}")
            return False

    def search_articles(self, query: str) -> List[Article]:
        """Search articles by title or summary."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                search_pattern = f"%{query}%"
                cursor.execute(
                    """
                    SELECT a.id, a.feed_id, a.title, a.link, a.summary,
                           a.author, a.published, a.is_read
                    FROM articles a
                    WHERE a.title LIKE ? OR a.summary LIKE ?
                    ORDER BY a.published DESC
                """,
                    (search_pattern, search_pattern),
                )

                rows = cursor.fetchall()
                articles = []
                for row in rows:
                    article = Article(
                        title=row[2],
                        link=row[3],
                        summary=row[4],
                        author=row[5],
                        published=(
                            datetime.datetime.fromisoformat(row[6]) if row[6] else None
                        ),
                        feed_id=row[1],
                        article_id=row[0],
                        is_read=bool(row[7]),
                    )
                    articles.append(article)

                return articles
        except sqlite3.Error as e:
            self.logger.error(f"Failed to search articles: {e}")
            return []

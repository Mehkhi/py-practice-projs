"""Core URL shortening functionality with SQLite storage."""

import hashlib
import logging
import random
import sqlite3
import string
from datetime import datetime, timedelta
from typing import Optional, Tuple

logger = logging.getLogger(__name__)


class URLShortener:
    """Main URL shortener class with SQLite backend."""

    def __init__(self, db_path: str = "urls.db") -> None:
        """Initialize the URL shortener with database path."""
        self.db_path = db_path
        self.init_database()

    def init_database(self) -> None:
        """Initialize the SQLite database with required tables."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS urls (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        short_code TEXT UNIQUE NOT NULL,
                        original_url TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        expires_at TIMESTAMP NULL,
                        click_count INTEGER DEFAULT 0,
                        custom_code BOOLEAN DEFAULT FALSE
                    )
                """
                )
                conn.commit()
                logger.info("Database initialized successfully")
        except sqlite3.Error as e:
            logger.error(f"Database initialization failed: {e}")
            raise

    def generate_short_code(self, length: int = 6) -> str:
        """Generate a random short code."""
        chars = string.ascii_letters + string.digits
        return "".join(random.choices(chars, k=length))

    def generate_hash_code(self, url: str, length: int = 6) -> str:
        """Generate a hash-based short code from URL."""
        hash_obj = hashlib.md5(url.encode())
        return hash_obj.hexdigest()[:length]

    def validate_url(self, url: str) -> bool:
        """Basic URL validation."""
        if not url or not isinstance(url, str):
            return False
        return url.startswith(("http://", "https://"))

    def is_expired(self, expires_at: Optional[str]) -> bool:
        """Check if a URL has expired."""
        if not expires_at:
            return False
        try:
            expiry_date = datetime.fromisoformat(expires_at)
            return datetime.now() > expiry_date
        except ValueError:
            return False

    def create_short_url(
        self,
        original_url: str,
        custom_code: Optional[str] = None,
        expires_days: Optional[int] = None,
        use_hash: bool = False,
    ) -> Tuple[str, str]:
        """
        Create a shortened URL.

        Returns:
            Tuple of (short_code, full_short_url)
        """
        if not self.validate_url(original_url):
            raise ValueError("Invalid URL format")

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Precompute expiration if requested
                expires_at = None
                if expires_days:
                    expires_at = (
                        datetime.now() + timedelta(days=expires_days)
                    ).isoformat()

                # Handle custom code
                if custom_code is not None:
                    if len(custom_code) < 3:
                        raise ValueError("Custom code must be at least 3 characters")

                    cursor.execute(
                        "SELECT id FROM urls WHERE short_code = ?", (custom_code,)
                    )
                    if cursor.fetchone():
                        raise ValueError("Custom code already exists")

                    short_code = custom_code
                    is_custom = True
                else:
                    # Generate unique code
                    attempts = 0
                    max_attempts = 100
                    short_code = None

                    if use_hash:
                        candidate = self.generate_hash_code(original_url)
                        cursor.execute(
                            "SELECT original_url, expires_at FROM urls WHERE short_code = ?",
                            (candidate,),
                        )
                        existing = cursor.fetchone()

                        if existing:
                            existing_url, existing_expires_at = existing

                            if existing_url == original_url:
                                # Refresh expiration when needed
                                new_expires_at = (
                                    expires_at
                                    if expires_at is not None
                                    else existing_expires_at
                                )

                                if (
                                    expires_at is None
                                    and existing_expires_at
                                    and self.is_expired(existing_expires_at)
                                ):
                                    new_expires_at = None

                                if new_expires_at != existing_expires_at:
                                    cursor.execute(
                                        """
                                        UPDATE urls
                                        SET expires_at = ?
                                        WHERE short_code = ?
                                    """,
                                        (new_expires_at, candidate),
                                    )
                                    conn.commit()

                                full_short_url = f"http://localhost:5000/{candidate}"
                                logger.info(
                                    "Reused existing hash short URL: %s -> %s",
                                    candidate,
                                    original_url,
                                )
                                return candidate, full_short_url

                            logger.warning(
                                "Hash collision for %s; generated code already in use by another URL",
                                original_url,
                            )
                        else:
                            short_code = candidate

                    while attempts < max_attempts:
                        if not short_code:
                            short_code = self.generate_short_code()

                        cursor.execute(
                            "SELECT id FROM urls WHERE short_code = ?", (short_code,)
                        )
                        if not cursor.fetchone():
                            break
                        attempts += 1
                        short_code = None
                    else:
                        raise RuntimeError("Failed to generate unique short code")

                    is_custom = False

                # Insert into database
                cursor.execute(
                    """
                    INSERT INTO urls (short_code, original_url, expires_at, custom_code)
                    VALUES (?, ?, ?, ?)
                """,
                    (short_code, original_url, expires_at, is_custom),
                )

                conn.commit()
                full_short_url = f"http://localhost:5000/{short_code}"
                logger.info(f"Created short URL: {short_code} -> {original_url}")

                return short_code, full_short_url

        except sqlite3.Error as e:
            logger.error(f"Database error creating short URL: {e}")
            raise

    def get_original_url(self, short_code: str) -> Optional[str]:
        """Get original URL by short code and increment click count."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute(
                    """
                    SELECT original_url, expires_at FROM urls
                    WHERE short_code = ?
                """,
                    (short_code,),
                )

                result = cursor.fetchone()
                if not result:
                    return None

                original_url, expires_at = result

                # Check expiration
                if self.is_expired(expires_at):
                    logger.info(f"Short URL {short_code} has expired")
                    return None

                # Increment click count
                cursor.execute(
                    """
                    UPDATE urls SET click_count = click_count + 1
                    WHERE short_code = ?
                """,
                    (short_code,),
                )

                conn.commit()
                logger.info(f"Redirected {short_code} to {original_url}")
                return original_url

        except sqlite3.Error as e:
            logger.error(f"Database error retrieving URL: {e}")
            return None

    def get_url_stats(self, short_code: str) -> Optional[dict]:
        """Get statistics for a short URL."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute(
                    """
                    SELECT short_code, original_url, created_at, expires_at,
                           click_count, custom_code
                    FROM urls WHERE short_code = ?
                """,
                    (short_code,),
                )

                result = cursor.fetchone()
                if not result:
                    return None

                return {
                    "short_code": result[0],
                    "original_url": result[1],
                    "created_at": result[2],
                    "expires_at": result[3],
                    "click_count": result[4],
                    "custom_code": bool(result[5]),
                    "expired": self.is_expired(result[3]),
                }

        except sqlite3.Error as e:
            logger.error(f"Database error getting stats: {e}")
            return None

    def list_all_urls(self) -> list:
        """List all URLs in the database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute(
                    """
                    SELECT short_code, original_url, created_at, expires_at,
                           click_count, custom_code
                    FROM urls ORDER BY created_at DESC
                """
                )

                results = []
                for row in cursor.fetchall():
                    results.append(
                        {
                            "short_code": row[0],
                            "original_url": row[1],
                            "created_at": row[2],
                            "expires_at": row[3],
                            "click_count": row[4],
                            "custom_code": bool(row[5]),
                            "expired": self.is_expired(row[3]),
                        }
                    )

                return results

        except sqlite3.Error as e:
            logger.error(f"Database error listing URLs: {e}")
            return []

    def delete_url(self, short_code: str) -> bool:
        """Delete a short URL."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute("DELETE FROM urls WHERE short_code = ?", (short_code,))
                deleted = cursor.rowcount > 0
                conn.commit()

                if deleted:
                    logger.info(f"Deleted short URL: {short_code}")

                return deleted

        except sqlite3.Error as e:
            logger.error(f"Database error deleting URL: {e}")
            return False

    def cleanup_expired(self) -> int:
        """Remove expired URLs and return count of deleted items."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute(
                    """
                    DELETE FROM urls
                    WHERE expires_at IS NOT NULL AND expires_at < ?
                """,
                    (datetime.now().isoformat(),),
                )

                deleted_count = cursor.rowcount
                conn.commit()

                if deleted_count > 0:
                    logger.info(f"Cleaned up {deleted_count} expired URLs")

                return deleted_count

        except sqlite3.Error as e:
            logger.error(f"Database error cleaning up expired URLs: {e}")
            return 0

    def get_connection(self):
        """Get a database connection for testing."""
        return sqlite3.connect(self.db_path)

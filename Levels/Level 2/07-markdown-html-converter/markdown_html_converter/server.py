"""
Live preview server for markdown files.
"""

import os
import webbrowser
import threading
import time
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
from typing import Optional

import logging

logger = logging.getLogger(__name__)


class MarkdownPreviewHandler(SimpleHTTPRequestHandler):
    """Custom handler for serving markdown preview files."""

    def __init__(self, *args, markdown_file: str, converter, **kwargs):
        self.markdown_file = markdown_file
        self.converter = converter
        super().__init__(*args, **kwargs)

    def do_GET(self):
        """Handle GET requests."""
        if self.path == '/' or self.path == '/index.html':
            # Convert markdown to HTML and serve
            try:
                html_content = self.converter.convert_text(
                    Path(self.markdown_file).read_text(encoding='utf-8')
                )

                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(html_content.encode('utf-8'))

            except Exception as e:
                logger.error(f"Error converting markdown: {e}")
                self.send_error(500, f"Error converting markdown: {e}")
        else:
            super().do_GET()

    def log_message(self, format, *args):
        """Override to reduce log noise."""
        pass


def start_preview_server(markdown_file: str, port: int = 8000,
                        converter=None, open_browser: bool = True) -> None:
    """
    Start a live preview server for a markdown file.

    Args:
        markdown_file: Path to the markdown file to preview
        port: Port to run the server on
        converter: MarkdownConverter instance
        open_browser: Whether to automatically open browser
    """
    if not os.path.exists(markdown_file):
        raise FileNotFoundError(f"Markdown file not found: {markdown_file}")

    # Create custom handler with converter
    def handler(*args, **kwargs):
        return MarkdownPreviewHandler(*args, markdown_file=markdown_file,
                                    converter=converter, **kwargs)

    # Start server
    server = HTTPServer(('localhost', port), handler)
    server_url = f"http://localhost:{port}"

    logger.info(f"Starting preview server on {server_url}")
    logger.info(f"Previewing: {markdown_file}")
    logger.info("Press Ctrl+C to stop the server")

    # Open browser in a separate thread
    if open_browser:
        def open_browser_delayed():
            time.sleep(1)  # Give server time to start
            webbrowser.open(server_url)

        browser_thread = threading.Thread(target=open_browser_delayed)
        browser_thread.daemon = True
        browser_thread.start()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
        server.shutdown()
    except Exception as e:
        logger.error(f"Server error: {e}")
        raise


def watch_file_changes(markdown_file: str, callback, check_interval: float = 1.0):
    """
    Watch a file for changes and call callback when it changes.

    Args:
        markdown_file: Path to file to watch
        callback: Function to call when file changes
        check_interval: How often to check for changes (seconds)
    """
    last_modified = 0

    while True:
        try:
            current_modified = os.path.getmtime(markdown_file)
            if current_modified > last_modified:
                last_modified = current_modified
                callback()
            time.sleep(check_interval)
        except FileNotFoundError:
            logger.error(f"File not found: {markdown_file}")
            break
        except KeyboardInterrupt:
            break
        except Exception as e:
            logger.error(f"Error watching file: {e}")
            break

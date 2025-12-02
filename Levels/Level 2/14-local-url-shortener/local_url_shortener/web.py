"""Web interface for the URL shortener using Flask."""

import logging

try:
    from flask import Flask, redirect, render_template_string, request, jsonify

    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False

logger = logging.getLogger(__name__)


# HTML templates
HOME_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Local URL Shortener</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #333;
            text-align: center;
        }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
        }
        input[type="text"], input[type="url"], input[type="number"] {
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 5px;
            box-sizing: border-box;
        }
        button {
            background-color: #007bff;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
        }
        button:hover {
            background-color: #0056b3;
        }
        .result {
            margin-top: 20px;
            padding: 15px;
            background-color: #e9ecef;
            border-radius: 5px;
            word-break: break-all;
        }
        .error {
            background-color: #f8d7da;
            color: #721c24;
        }
        .success {
            background-color: #d4edda;
            color: #155724;
        }
        .stats {
            margin-top: 30px;
            padding: 20px;
            background-color: #f8f9fa;
            border-radius: 5px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 10px;
        }
        th, td {
            padding: 10px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }
        th {
            background-color: #007bff;
            color: white;
        }
        .short-url {
            font-family: monospace;
            background-color: #e9ecef;
            padding: 2px 5px;
            border-radius: 3px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔗 Local URL Shortener</h1>

        <form method="POST" action="/shorten">
            <div class="form-group">
                <label for="url">URL to shorten:</label>
                <input type="url" id="url" name="url" required placeholder="https://example.com">
            </div>

            <div class="form-group">
                <label for="custom_code">Custom code (optional):</label>
                <input type="text" id="custom_code" name="custom_code" placeholder="mylink">
            </div>

            <div class="form-group">
                <label for="expires_days">Expires in days (optional):</label>
                <input type="number" id="expires_days" name="expires_days" min="1" placeholder="30">
            </div>

            <button type="submit">Shorten URL</button>
        </form>

        {% if message %}
        <div class="result {{ message_type }}">
            {{ message }}
        </div>
        {% endif %}

        <div class="stats">
            <h3>📊 Recent URLs</h3>
            {% if urls %}
            <table>
                <thead>
                    <tr>
                        <th>Short Code</th>
                        <th>Original URL</th>
                        <th>Clicks</th>
                        <th>Created</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>
                    {% for url in urls %}
                    <tr>
                        <td><span class="short-url">{{ url.short_code }}</span></td>
                        <td>{{ url.original_url[:50] }}{% if url.original_url|length > 50 %}...{% endif %}</td>
                        <td>{{ url.click_count }}</td>
                        <td>{{ url.created_at[:10] }}</td>
                        <td>
                            {% if url.expired %}
                                <span style="color: red;">Expired</span>
                            {% elif url.expires_at %}
                                <span style="color: orange;">Active</span>
                            {% else %}
                                <span style="color: green;">Permanent</span>
                            {% endif %}
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
            {% else %}
            <p>No URLs created yet.</p>
            {% endif %}
        </div>
    </div>
</body>
</html>
"""


def create_app(shortener) -> Flask:
    """
    Create and configure the Flask application.

    Args:
        shortener: URLShortener instance

    Returns:
        Configured Flask application
    """
    if not FLASK_AVAILABLE:
        raise ImportError("Flask not installed. Install with: pip install flask")

    app = Flask(__name__)
    app.config["SECRET_KEY"] = "dev-key-change-in-production"

    @app.route("/")
    def home():
        """Home page with URL shortening form."""
        urls = shortener.list_all_urls()[:10]  # Show last 10 URLs
        return render_template_string(HOME_TEMPLATE, urls=urls)

    @app.route("/shorten", methods=["POST"])
    def shorten_url():
        """Handle URL shortening form submission."""
        url = request.form.get("url", "").strip()
        custom_code = request.form.get("custom_code", "").strip() or None
        expires_days = request.form.get("expires_days", "").strip()

        if expires_days:
            try:
                expires_days = int(expires_days)
            except ValueError:
                expires_days = None
        else:
            expires_days = None

        try:
            short_code, full_url = shortener.create_short_url(
                url, custom_code=custom_code, expires_days=expires_days
            )

            message = f"✅ Short URL created: <a href='{full_url}' target='_blank'>{full_url}</a>"
            urls = shortener.list_all_urls()[:10]

            return render_template_string(
                HOME_TEMPLATE, message=message, message_type="success", urls=urls
            )

        except ValueError as e:
            message = f"❌ Error: {str(e)}"
            urls = shortener.list_all_urls()[:10]

            return render_template_string(
                HOME_TEMPLATE, message=message, message_type="error", urls=urls
            )
        except Exception as e:
            logger.error(f"Unexpected error in shorten_url: {e}")
            message = "❌ An unexpected error occurred"
            urls = shortener.list_all_urls()[:10]

            return render_template_string(
                HOME_TEMPLATE, message=message, message_type="error", urls=urls
            )

    @app.route("/<short_code>")
    def redirect_url(short_code: str):
        """Redirect to original URL."""
        original_url = shortener.get_original_url(short_code)

        if original_url:
            logger.info(f"Redirecting {short_code} to {original_url}")
            return redirect(original_url)
        else:
            # Custom 404 page
            return (
                render_template_string(
                    """
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>URL Not Found</title>
                <style>
                    body {
                        font-family: Arial, sans-serif;
                        text-align: center;
                        padding: 50px;
                        background-color: #f5f5f5;
                    }
                    .container {
                        background: white;
                        padding: 40px;
                        border-radius: 10px;
                        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                        max-width: 500px;
                        margin: 0 auto;
                    }
                    h1 {
                        color: #dc3545;
                    }
                    a {
                        color: #007bff;
                        text-decoration: none;
                    }
                    a:hover {
                        text-decoration: underline;
                    }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>🔗 URL Not Found</h1>
                    <p>The short code <strong>{{ short_code }}</strong> was not found or has expired.</p>
                    <p><a href="/">Return to home</a></p>
                </div>
            </body>
            </html>
            """,
                    short_code=short_code,
                ),
                404,
            )

    @app.route("/api/shorten", methods=["POST"])
    def api_shorten():
        """API endpoint for URL shortening."""
        data = request.get_json()

        if not data or "url" not in data:
            return jsonify({"error": "URL is required"}), 400

        url = data["url"].strip()
        custom_code = data.get("custom_code", "").strip() or None
        expires_input = data.get("expires_days")

        expires_days = None
        if expires_input is not None:
            if isinstance(expires_input, str):
                expires_input = expires_input.strip()
                if expires_input:
                    if not expires_input.isdigit():
                        return (
                            jsonify(
                                {
                                    "error": "expires_days must be a non-negative integer"
                                }
                            ),
                            400,
                        )
                    expires_days = int(expires_input)
            elif isinstance(expires_input, (int, float)):
                if expires_input < 0:
                    return (
                        jsonify(
                            {
                                "error": "expires_days must be a non-negative integer"
                            }
                        ),
                        400,
                    )
                expires_days = int(expires_input)
            else:
                return (
                    jsonify(
                        {"error": "expires_days must be provided as a number or string"}
                    ),
                    400,
                )

        try:
            short_code, full_url = shortener.create_short_url(
                url, custom_code=custom_code, expires_days=expires_days
            )

            return jsonify(
                {
                    "short_code": short_code,
                    "short_url": full_url,
                    "original_url": url,
                    "expires_days": expires_days,
                }
            )

        except ValueError as e:
            return jsonify({"error": str(e)}), 400
        except Exception as e:
            logger.error(f"API error: {e}")
            return jsonify({"error": "Internal server error"}), 500

    @app.route("/api/<short_code>")
    def api_expand(short_code: str):
        """API endpoint to expand short URL."""
        original_url = shortener.get_original_url(short_code)

        if original_url:
            return jsonify({"short_code": short_code, "original_url": original_url})
        else:
            return jsonify({"error": "Short code not found or expired"}), 404

    @app.route("/api/<short_code>/stats")
    def api_stats(short_code: str):
        """API endpoint to get URL statistics."""
        stats = shortener.get_url_stats(short_code)

        if stats:
            return jsonify(stats)
        else:
            return jsonify({"error": "Short code not found"}), 404

    @app.route("/api/urls")
    def api_list():
        """API endpoint to list all URLs."""
        urls = shortener.list_all_urls()
        return jsonify({"urls": urls})

    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 errors."""
        return (
            render_template_string(
                """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Page Not Found</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    text-align: center;
                    padding: 50px;
                    background-color: #f5f5f5;
                }
                .container {
                    background: white;
                    padding: 40px;
                    border-radius: 10px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    max-width: 500px;
                    margin: 0 auto;
                }
                h1 {
                    color: #dc3545;
                }
                a {
                    color: #007bff;
                    text-decoration: none;
                }
                a:hover {
                    text-decoration: underline;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>404 - Page Not Found</h1>
                <p>The page you're looking for doesn't exist.</p>
                <p><a href="/">Return to home</a></p>
            </div>
        </body>
        </html>
        """
            ),
            404,
        )

    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 errors."""
        logger.error(f"Internal server error: {error}")
        return (
            render_template_string(
                """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Server Error</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    text-align: center;
                    padding: 50px;
                    background-color: #f5f5f5;
                }
                .container {
                    background: white;
                    padding: 40px;
                    border-radius: 10px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    max-width: 500px;
                    margin: 0 auto;
                }
                h1 {
                    color: #dc3545;
                }
                a {
                    color: #007bff;
                    text-decoration: none;
                }
                a:hover {
                    text-decoration: underline;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>500 - Server Error</h1>
                <p>Something went wrong on our end.</p>
                <p><a href="/">Return to home</a></p>
            </div>
        </body>
        </html>
        """
            ),
            500,
        )

    return app

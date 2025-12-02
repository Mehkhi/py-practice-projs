"""Utility functions for web log analyzer."""

import csv
import json
import logging
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime


def setup_logging(level: str = "INFO") -> None:
    """Set up logging configuration."""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def format_bytes(bytes_count: int) -> str:
    """Format bytes into human-readable string."""
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if bytes_count < 1024.0:
            return f"{bytes_count:.2f} {unit}"
        bytes_count /= 1024.0
    return f"{bytes_count:.2f} PB"


def format_duration(seconds: float) -> str:
    """Format duration in seconds to human-readable string."""
    if seconds < 60:
        return f"{seconds:.2f} seconds"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.2f} minutes"
    else:
        hours = seconds / 3600
        return f"{hours:.2f} hours"


def validate_log_file(file_path: str) -> bool:
    """Validate that the log file exists and is readable."""
    path = Path(file_path)
    if not path.exists():
        logging.error(f"Log file does not exist: {file_path}")
        return False
    if not path.is_file():
        logging.error(f"Path is not a file: {file_path}")
        return False
    if not path.stat().st_size > 0:
        logging.error(f"Log file is empty: {file_path}")
        return False
    return True


def write_text_report(analysis_results: Dict[str, Any], output_file: str) -> None:
    """Write analysis results to a text file."""
    try:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("Web Log Analysis Report\n")
            f.write("=" * 50 + "\n")
            f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            # Basic Statistics
            if "basic_stats" in analysis_results:
                stats = analysis_results["basic_stats"]
                f.write("Basic Statistics\n")
                f.write("-" * 20 + "\n")
                f.write(f"Total Requests: {stats.get('total_requests', 0):,}\n")
                f.write(f"Unique IPs: {stats.get('unique_ips', 0):,}\n")
                f.write(
                    f"Total Bytes Served: {format_bytes(stats.get('total_bytes_served', 0))}\n"
                )
                f.write(
                    f"Average Bytes per Request: {format_bytes(stats.get('avg_bytes_per_request', 0))}\n"
                )

                if "time_range" in stats:
                    time_range = stats["time_range"]
                    f.write(
                        f"Time Range: {time_range.get('start', 'N/A')} to {time_range.get('end', 'N/A')}\n"
                    )
                    f.write(
                        f"Duration: {format_duration(time_range.get('duration_hours', 0) * 3600)}\n"
                    )

                f.write("\n")

            # Status Distribution
            if (
                "basic_stats" in analysis_results
                and "status_distribution" in analysis_results["basic_stats"]
            ):
                f.write("Status Code Distribution\n")
                f.write("-" * 25 + "\n")
                for status, count in analysis_results["basic_stats"][
                    "status_distribution"
                ].items():
                    f.write(f"{status}: {count:,}\n")
                f.write("\n")

            # Top Endpoints
            if "top_endpoints" in analysis_results:
                f.write("Top Endpoints\n")
                f.write("-" * 15 + "\n")
                for i, (endpoint, count) in enumerate(
                    analysis_results["top_endpoints"], 1
                ):
                    f.write(f"{i:2d}. {endpoint}: {count:,} requests\n")
                f.write("\n")

            # Top IPs
            if "top_ips" in analysis_results:
                f.write("Top IP Addresses\n")
                f.write("-" * 18 + "\n")
                for i, (ip, count) in enumerate(analysis_results["top_ips"], 1):
                    f.write(f"{i:2d}. {ip}: {count:,} requests\n")
                f.write("\n")

            # Error Analysis
            if "error_analysis" in analysis_results:
                errors = analysis_results["error_analysis"]
                f.write("Error Analysis\n")
                f.write("-" * 15 + "\n")
                f.write(f"Total Errors: {errors.get('total_errors', 0):,}\n")
                f.write(f"Error Rate: {errors.get('error_rate', 0):.2f}%\n")

                if "not_found_analysis" in errors:
                    not_found = errors["not_found_analysis"]
                    f.write(f"404 Not Found: {not_found.get('total_404s', 0):,}\n")

                    if "top_missing_paths" in not_found:
                        f.write("\nTop Missing Paths (404s):\n")
                        for i, (path, count) in enumerate(
                            not_found["top_missing_paths"][:5], 1
                        ):
                            f.write(f"{i:2d}. {path}: {count:,}\n")
                f.write("\n")

            # Traffic Patterns
            if "traffic_patterns" in analysis_results:
                patterns = analysis_results["traffic_patterns"]
                f.write("Traffic Patterns\n")
                f.write("-" * 17 + "\n")

                if "peak_hour" in patterns and patterns["peak_hour"]:
                    hour, count = patterns["peak_hour"]
                    f.write(f"Peak Hour: {hour:02d}:00 with {count:,} requests\n")

                if "peak_day" in patterns and patterns["peak_day"]:
                    day, count = patterns["peak_day"]
                    f.write(f"Peak Day: {day} with {count:,} requests\n")
                f.write("\n")

            # Performance Analysis
            if "performance_analysis" in analysis_results:
                perf = analysis_results["performance_analysis"]
                if "message" not in perf:
                    f.write("Performance Analysis\n")
                    f.write("-" * 20 + "\n")
                    f.write(
                        f"Average Response Time: {perf.get('avg_response_time', 0):.3f}s\n"
                    )
                    f.write(
                        f"Min Response Time: {perf.get('min_response_time', 0):.3f}s\n"
                    )
                    f.write(
                        f"Max Response Time: {perf.get('max_response_time', 0):.3f}s\n"
                    )

                    if "slow_requests" in perf:
                        slow = perf["slow_requests"]
                        f.write(
                            f"Slow Requests (> {slow['threshold_seconds']}s): {slow['count']:,} ({slow['percentage']:.1f}%)\n"
                        )
                    f.write("\n")

            # User Agent Analysis
            if "user_agent_analysis" in analysis_results:
                ua = analysis_results["user_agent_analysis"]
                f.write("User Agent Analysis\n")
                f.write("-" * 21 + "\n")
                f.write(
                    f"Unique User Agents: {ua.get('total_unique_user_agents', 0):,}\n"
                )

                if "bot_traffic" in ua:
                    bot = ua["bot_traffic"]
                    f.write(
                        f"Bot Traffic: {bot.get('total_bot_requests', 0):,} requests ({bot.get('bot_percentage', 0):.1f}%)\n"
                    )

                if "browser_distribution" in ua:
                    f.write("\nBrowser Distribution:\n")
                    for browser, count in ua["browser_distribution"].items():
                        f.write(f"  {browser}: {count:,}\n")

        logging.info(f"Text report written to: {output_file}")

    except Exception as e:
        logging.error(f"Failed to write text report: {e}")
        raise


def write_csv_report(analysis_results: Dict[str, Any], output_file: str) -> None:
    """Write analysis results to a CSV file."""
    try:
        with open(output_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)

            # Write header
            writer.writerow(["Metric", "Value"])

            # Basic Statistics
            if "basic_stats" in analysis_results:
                stats = analysis_results["basic_stats"]
                writer.writerow(["Total Requests", stats.get("total_requests", 0)])
                writer.writerow(["Unique IPs", stats.get("unique_ips", 0)])
                writer.writerow(
                    ["Total Bytes Served", stats.get("total_bytes_served", 0)]
                )
                writer.writerow(
                    [
                        "Average Bytes per Request",
                        f"{stats.get('avg_bytes_per_request', 0):.2f}",
                    ]
                )

                if "time_range" in stats:
                    time_range = stats["time_range"]
                    writer.writerow(["Start Time", time_range.get("start", "N/A")])
                    writer.writerow(["End Time", time_range.get("end", "N/A")])
                    writer.writerow(
                        [
                            "Duration (hours)",
                            f"{time_range.get('duration_hours', 0):.2f}",
                        ]
                    )

                # Status Distribution
                if "status_distribution" in stats:
                    for status, count in stats["status_distribution"].items():
                        writer.writerow([f"Status {status}", count])

            # Top Endpoints
            if "top_endpoints" in analysis_results:
                writer.writerow(["", ""])  # Empty row for separation
                writer.writerow(["Top Endpoints", "Requests"])
                for endpoint, count in analysis_results["top_endpoints"]:
                    writer.writerow([endpoint, count])

            # Top IPs
            if "top_ips" in analysis_results:
                writer.writerow(["", ""])  # Empty row for separation
                writer.writerow(["Top IP Addresses", "Requests"])
                for ip, count in analysis_results["top_ips"]:
                    writer.writerow([ip, count])

            # Error Analysis
            if "error_analysis" in analysis_results:
                errors = analysis_results["error_analysis"]
                writer.writerow(["", ""])  # Empty row for separation
                writer.writerow(["Error Metrics", "Value"])
                writer.writerow(["Total Errors", errors.get("total_errors", 0)])
                writer.writerow(
                    ["Error Rate (%)", f"{errors.get('error_rate', 0):.2f}"]
                )

                if "not_found_analysis" in errors:
                    not_found = errors["not_found_analysis"]
                    writer.writerow(["404 Not Found", not_found.get("total_404s", 0)])

        logging.info(f"CSV report written to: {output_file}")

    except Exception as e:
        logging.error(f"Failed to write CSV report: {e}")
        raise


def write_json_report(analysis_results: Dict[str, Any], output_file: str) -> None:
    """Write analysis results to a JSON file."""
    try:
        # Convert datetime objects to strings for JSON serialization
        def json_serializer(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(analysis_results, f, indent=2, default=json_serializer)

        logging.info(f"JSON report written to: {output_file}")

    except Exception as e:
        logging.error(f"Failed to write JSON report: {e}")
        raise


def detect_log_format(sample_lines: List[str]) -> str:
    """Detect log format based on sample lines."""
    import re
    from .core import LogParser

    formats_to_try = [
        ("nginx_time", LogParser.NGINX_WITH_TIME),
        ("combined", LogParser.APACHE_COMBINED),
        ("nginx", LogParser.NGINX_DEFAULT),
        ("common", LogParser.APACHE_COMMON),
    ]

    for format_name, pattern in formats_to_try:
        matches = 0
        for line in sample_lines[:10]:  # Check first 10 lines
            if re.match(pattern, line.strip()):
                matches += 1

        if matches >= len(sample_lines[:10]) * 0.8:  # 80% match rate
            return format_name

    return "combined"  # Default fallback


def create_sample_log() -> str:
    """Create a sample log entry for testing."""
    return '127.0.0.1 - - [25/Dec/2023:10:00:00 +0000] "GET /index.html HTTP/1.1" 200 1234 "http://example.com" "Mozilla/5.0"'

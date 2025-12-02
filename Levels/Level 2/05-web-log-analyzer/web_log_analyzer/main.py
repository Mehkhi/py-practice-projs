"""Main entry point for the web log analyzer CLI."""

import argparse
import logging
import sys
from pathlib import Path
from typing import List, Optional

from .core import LogParser, LogAnalyzer
from .utils import (
    setup_logging,
    validate_log_file,
    write_text_report,
    write_csv_report,
    write_json_report,
    detect_log_format,
    create_sample_log,
)


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Analyze Apache/Nginx web server access logs",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s access.log
  %(prog)s access.log --format nginx --output report.txt
  %(prog)s access.log --output-dir reports/ --format combined
  %(prog)s --sample  # Generate sample log for testing
        """,
    )

    parser.add_argument("log_file", nargs="?", help="Path to the log file to analyze")

    parser.add_argument(
        "--format",
        "-f",
        choices=["common", "combined", "nginx", "nginx_time", "auto"],
        default="auto",
        help="Log format (default: auto-detect)",
    )

    parser.add_argument("--output", "-o", help="Output file path (default: stdout)")

    parser.add_argument(
        "--output-dir", help="Output directory for multiple format reports"
    )

    parser.add_argument(
        "--format-output",
        choices=["text", "csv", "json", "all"],
        default="text",
        help="Output format (default: text)",
    )

    parser.add_argument(
        "--top",
        "-t",
        type=int,
        default=10,
        help="Number of top items to show (default: 10)",
    )

    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose logging"
    )

    parser.add_argument(
        "--quiet", "-q", action="store_true", help="Suppress non-error output"
    )

    parser.add_argument(
        "--sample", action="store_true", help="Generate a sample log entry and exit"
    )

    parser.add_argument(
        "--include-performance",
        action="store_true",
        help="Include performance analysis (requires response time data)",
    )

    return parser.parse_args()


def read_log_file(file_path: str, max_lines: Optional[int] = None) -> List[str]:
    """Read log file and return lines."""
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            if max_lines:
                return [line.rstrip("\n") for line in f.readlines(max_lines)]
            return [line.rstrip("\n") for line in f]
    except Exception as e:
        logging.error(f"Failed to read log file {file_path}: {e}")
        raise


def analyze_logs(
    log_lines: List[str],
    log_format: str,
    top_count: int,
    include_performance: bool = False,
) -> dict:
    """Analyze log lines and return results."""
    # Detect format if needed
    if log_format == "auto":
        log_format = detect_log_format(log_lines)
        logging.info(f"Auto-detected log format: {log_format}")

    # Parse logs
    parser = LogParser(log_format)
    analyzer = LogAnalyzer()

    entries = []
    for i, line in enumerate(log_lines):
        entry = parser.parse_line(line)
        if entry:
            entries.append(entry)

        if i > 0 and i % 10000 == 0:
            logging.info(f"Parsed {i} lines...")

    if not entries:
        logging.warning("No valid log entries found")
        return {}

    analyzer.add_entries(entries)

    # Generate analysis
    results = {
        "basic_stats": analyzer.get_basic_stats(),
        "top_endpoints": analyzer.get_top_endpoints(top_count),
        "top_ips": analyzer.get_top_ips(top_count),
        "error_analysis": analyzer.get_error_analysis(),
        "traffic_patterns": analyzer.get_traffic_patterns(),
        "user_agent_analysis": analyzer.get_user_agent_analysis(),
    }

    if include_performance:
        results["performance_analysis"] = analyzer.get_performance_analysis()

    return results


def print_summary(results: dict, output_format: str = "text") -> None:
    """Print a summary of analysis results to stdout."""
    if not results:
        print("No analysis results to display")
        return

    if output_format == "json":
        import json

        print(json.dumps(results, indent=2, default=str))
        return

    # Text summary
    print("Web Log Analysis Summary")
    print("=" * 40)

    if "basic_stats" in results:
        stats = results["basic_stats"]
        print(f"Total Requests: {stats.get('total_requests', 0):,}")
        print(f"Unique IPs: {stats.get('unique_ips', 0):,}")

        if "time_range" in stats:
            time_range = stats["time_range"]
            print(
                f"Time Range: {time_range.get('start', 'N/A')} to {time_range.get('end', 'N/A')}"
            )

        print(f"Total Bytes: {stats.get('total_bytes_served', 0):,}")

    if "error_analysis" in results:
        errors = results["error_analysis"]
        print(
            f"Errors: {errors.get('total_errors', 0):,} ({errors.get('error_rate', 0):.1f}%)"
        )

    if "top_endpoints" in results:
        print("\nTop Endpoints:")
        for i, (endpoint, count) in enumerate(results["top_endpoints"][:5], 1):
            print(f"  {i}. {endpoint}: {count:,}")

    if "top_ips" in results:
        print("\nTop IPs:")
        for i, (ip, count) in enumerate(results["top_ips"][:5], 1):
            print(f"  {i}. {ip}: {count:,}")


def main() -> int:
    """Main entry point."""
    args = parse_arguments()

    # Setup logging
    if args.quiet:
        log_level = "ERROR"
    elif args.verbose:
        log_level = "DEBUG"
    else:
        log_level = "INFO"

    setup_logging(log_level)

    # Handle sample generation
    if args.sample:
        print(create_sample_log())
        return 0

    # Validate arguments
    if not args.log_file:
        print("Error: Log file path is required", file=sys.stderr)
        print("Use --sample to generate a sample log entry", file=sys.stderr)
        return 1

    # Validate log file
    if not validate_log_file(args.log_file):
        return 1

    try:
        # Read log file
        logging.info(f"Reading log file: {args.log_file}")
        log_lines = read_log_file(args.log_file)
        logging.info(f"Read {len(log_lines)} lines from log file")

        # Analyze logs
        logging.info("Analyzing log entries...")
        results = analyze_logs(
            log_lines, args.format, args.top, args.include_performance
        )

        if not results:
            print("No valid log entries found in the file", file=sys.stderr)
            return 1

        # Output results
        if args.output or args.output_dir:
            # Write to file(s)
            if args.output_dir:
                output_dir = Path(args.output_dir)
                output_dir.mkdir(parents=True, exist_ok=True)

                base_name = Path(args.log_file).stem

                if args.format_output in ["text", "all"]:
                    text_file = output_dir / f"{base_name}_report.txt"
                    write_text_report(results, str(text_file))

                if args.format_output in ["csv", "all"]:
                    csv_file = output_dir / f"{base_name}_report.csv"
                    write_csv_report(results, str(csv_file))

                if args.format_output in ["json", "all"]:
                    json_file = output_dir / f"{base_name}_report.json"
                    write_json_report(results, str(json_file))

                if not args.quiet:
                    print(f"Reports written to: {output_dir}")

            else:
                # Single output file
                if args.format_output == "text":
                    write_text_report(results, args.output)
                elif args.format_output == "csv":
                    write_csv_report(results, args.output)
                elif args.format_output == "json":
                    write_json_report(results, args.output)

                if not args.quiet:
                    print(f"Report written to: {args.output}")

        else:
            # Print to stdout
            print_summary(results, args.format_output)

        return 0

    except KeyboardInterrupt:
        logging.info("Analysis interrupted by user")
        return 130
    except Exception as e:
        logging.error(f"Analysis failed: {e}")
        if args.verbose:
            import traceback

            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

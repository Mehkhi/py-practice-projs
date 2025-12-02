"""Comprehensive tests for web_log_analyzer."""

import pytest
import tempfile
import os
from datetime import datetime

from web_log_analyzer.core import LogParser, LogAnalyzer, LogEntry
from web_log_analyzer.utils import (
    format_bytes,
    format_duration,
    validate_log_file,
    detect_log_format,
    write_text_report,
    write_csv_report,
    write_json_report,
)
from web_log_analyzer.main import analyze_logs, read_log_file


class TestLogParser:
    """Test cases for LogParser class."""

    def test_apache_combined_parsing(self):
        """Test parsing Apache combined log format."""
        parser = LogParser("combined")
        log_line = '127.0.0.1 - - [25/Dec/2023:10:00:00 +0000] "GET /index.html HTTP/1.1" 200 1234 "http://example.com" "Mozilla/5.0"'

        entry = parser.parse_line(log_line)

        assert entry is not None
        assert entry.ip == "127.0.0.1"
        assert entry.method == "GET"
        assert entry.path == "/index.html"
        assert entry.status_code == 200
        assert entry.size == 1234
        assert entry.user_agent == "Mozilla/5.0"
        assert entry.referer == "http://example.com"

    def test_nginx_parsing(self):
        """Test parsing Nginx log format."""
        parser = LogParser("nginx")
        log_line = '192.168.1.1 - user [25/Dec/2023:10:00:00 +0000] "POST /api/data HTTP/1.1" 404 567 "http://example.com" "curl/7.68.0"'

        entry = parser.parse_line(log_line)

        assert entry is not None
        assert entry.ip == "192.168.1.1"
        assert entry.method == "POST"
        assert entry.path == "/api/data"
        assert entry.status_code == 404
        assert entry.size == 567

    def test_nginx_with_response_time(self):
        """Test parsing Nginx log format with response time."""
        parser = LogParser("nginx_time")
        log_line = '10.0.0.1 - - [25/Dec/2023:10:00:00 +0000] "GET /api/slow HTTP/1.1" 200 2048 "-" "Python-requests/2.25.1" 1234567'

        entry = parser.parse_line(log_line)

        assert entry is not None
        assert entry.ip == "10.0.0.1"
        assert entry.response_time == 1.234567  # Convert from microseconds

    def test_invalid_line(self):
        """Test parsing invalid log lines."""
        parser = LogParser("combined")
        invalid_line = "This is not a valid log line"

        entry = parser.parse_line(invalid_line)
        assert entry is None

    def test_empty_line(self):
        """Test parsing empty lines."""
        parser = LogParser("combined")

        entry = parser.parse_line("")
        assert entry is None

        entry = parser.parse_line("   ")
        assert entry is None

    def test_comment_line(self):
        """Test parsing comment lines."""
        parser = LogParser("combined")

        entry = parser.parse_line("# This is a comment")
        assert entry is None

    def test_size_parsing(self):
        """Test size field parsing."""
        parser = LogParser("combined")

        # Test normal size
        log_line = '127.0.0.1 - - [25/Dec/2023:10:00:00 +0000] "GET /file.txt HTTP/1.1" 200 1024 "-" "-"'
        entry = parser.parse_line(log_line)
        assert entry.size == 1024

        # Test dash (no size)
        log_line = '127.0.0.1 - - [25/Dec/2023:10:00:00 +0000] "GET /no-size HTTP/1.1" 200 - "-" "-"'
        entry = parser.parse_line(log_line)
        assert entry.size == 0


class TestLogAnalyzer:
    """Test cases for LogAnalyzer class."""

    def setup_method(self):
        """Set up test data."""
        self.analyzer = LogAnalyzer()
        self.sample_entries = [
            LogEntry(
                ip="127.0.0.1",
                timestamp=datetime(2023, 12, 25, 10, 0, 0),
                method="GET",
                path="/index.html",
                status_code=200,
                size=1234,
                user_agent="Mozilla/5.0",
                referer="http://example.com",
            ),
            LogEntry(
                ip="192.168.1.1",
                timestamp=datetime(2023, 12, 25, 10, 1, 0),
                method="POST",
                path="/api/data",
                status_code=404,
                size=567,
                user_agent="curl/7.68.0",
                referer="-",
            ),
            LogEntry(
                ip="127.0.0.1",
                timestamp=datetime(2023, 12, 25, 10, 2, 0),
                method="GET",
                path="/about.html",
                status_code=200,
                size=2345,
                user_agent="Mozilla/5.0",
                referer="http://example.com",
            ),
        ]
        self.analyzer.add_entries(self.sample_entries)

    def test_basic_stats(self):
        """Test basic statistics calculation."""
        stats = self.analyzer.get_basic_stats()

        assert stats["total_requests"] == 3
        assert stats["unique_ips"] == 2
        assert stats["total_bytes_served"] == 1234 + 567 + 2345
        assert stats["status_distribution"] == {200: 2, 404: 1}
        assert stats["method_distribution"] == {"GET": 2, "POST": 1}

    def test_top_endpoints(self):
        """Test top endpoints calculation."""
        top_endpoints = self.analyzer.get_top_endpoints(5)

        assert len(top_endpoints) == 3
        assert top_endpoints[0] == ("/index.html", 1)
        assert top_endpoints[1] == ("/api/data", 1)
        assert top_endpoints[2] == ("/about.html", 1)

    def test_top_ips(self):
        """Test top IPs calculation."""
        top_ips = self.analyzer.get_top_ips(5)

        assert len(top_ips) == 2
        assert top_ips[0] == ("127.0.0.1", 2)
        assert top_ips[1] == ("192.168.1.1", 1)

    def test_error_analysis(self):
        """Test error analysis."""
        errors = self.analyzer.get_error_analysis()

        assert errors["total_errors"] == 1
        assert errors["error_rate"] == 33.33333333333333
        assert errors["status_distribution"] == {404: 1}
        assert errors["not_found_analysis"]["total_404s"] == 1

    def test_traffic_patterns(self):
        """Test traffic pattern analysis."""
        patterns = self.analyzer.get_traffic_patterns()

        assert patterns["hourly_distribution"] == {10: 3}
        assert patterns["daily_distribution"] == {"Monday": 3}
        assert patterns["peak_hour"] == (10, 3)
        assert patterns["peak_day"] == ("Monday", 3)

    def test_empty_analyzer(self):
        """Test analyzer with no entries."""
        empty_analyzer = LogAnalyzer()

        assert empty_analyzer.get_basic_stats() == {}
        assert empty_analyzer.get_top_endpoints() == []
        assert empty_analyzer.get_top_ips() == []
        assert empty_analyzer.get_error_analysis() == {"total_errors": 0}

    def test_performance_analysis_with_time_data(self):
        """Test performance analysis with response time data."""
        # Add entries with response times
        entries_with_time = [
            LogEntry(
                ip="127.0.0.1",
                timestamp=datetime(2023, 12, 25, 10, 0, 0),
                method="GET",
                path="/fast.html",
                status_code=200,
                size=100,
                user_agent="Mozilla/5.0",
                referer="-",
                response_time=0.1,
            ),
            LogEntry(
                ip="127.0.0.1",
                timestamp=datetime(2023, 12, 25, 10, 1, 0),
                method="GET",
                path="/slow.html",
                status_code=200,
                size=200,
                user_agent="Mozilla/5.0",
                referer="-",
                response_time=2.5,
            ),
        ]

        analyzer = LogAnalyzer()
        analyzer.add_entries(entries_with_time)

        perf = analyzer.get_performance_analysis()

        assert perf["total_requests_with_time"] == 2
        assert perf["avg_response_time"] == 1.3
        assert perf["min_response_time"] == 0.1
        assert perf["max_response_time"] == 2.5
        assert perf["slow_requests"]["count"] == 1
        assert perf["slow_requests"]["percentage"] == 50.0


class TestUtils:
    """Test cases for utility functions."""

    def test_format_bytes(self):
        """Test byte formatting."""
        assert format_bytes(0) == "0.00 B"
        assert format_bytes(1024) == "1.00 KB"
        assert format_bytes(1048576) == "1.00 MB"
        assert format_bytes(1073741824) == "1.00 GB"

    def test_format_duration(self):
        """Test duration formatting."""
        assert format_duration(30) == "30.00 seconds"
        assert format_duration(90) == "1.50 minutes"
        assert format_duration(7200) == "2.00 hours"

    def test_validate_log_file(self):
        """Test log file validation."""
        # Test with temporary file
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            f.write("test log line\n")
            temp_file = f.name

        try:
            assert validate_log_file(temp_file) is True
        finally:
            os.unlink(temp_file)

        # Test with non-existent file
        assert validate_log_file("/non/existent/file.log") is False

    def test_detect_log_format(self):
        """Test log format detection."""
        apache_lines = [
            '127.0.0.1 - - [25/Dec/2023:10:00:00 +0000] "GET /index.html HTTP/1.1" 200 1234 "http://example.com" "Mozilla/5.0"',
            '192.168.1.1 - - [25/Dec/2023:10:01:00 +0000] "POST /api/data HTTP/1.1" 404 567 "-" "curl/7.68.0"',
        ]

        nginx_time_lines = [
            '127.0.0.1 - - [25/Dec/2023:10:00:00 +0000] "GET /index.html HTTP/1.1" 200 1234 "http://example.com" "Mozilla/5.0" 1234567',
        ]

        assert detect_log_format(apache_lines) == "combined"
        assert detect_log_format(nginx_time_lines) == "nginx_time"

    def test_write_reports(self):
        """Test report writing functions."""
        sample_results = {
            "basic_stats": {
                "total_requests": 100,
                "unique_ips": 50,
                "total_bytes_served": 1000000,
                "status_distribution": {200: 80, 404: 20},
            },
            "top_endpoints": [("/index.html", 50), ("/api/data", 30)],
            "top_ips": [("127.0.0.1", 20), ("192.168.1.1", 15)],
            "error_analysis": {
                "total_errors": 20,
                "error_rate": 20.0,
                "not_found_analysis": {"total_404s": 20},
            },
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            # Test text report
            text_file = os.path.join(temp_dir, "report.txt")
            write_text_report(sample_results, text_file)
            assert os.path.exists(text_file)

            # Test CSV report
            csv_file = os.path.join(temp_dir, "report.csv")
            write_csv_report(sample_results, csv_file)
            assert os.path.exists(csv_file)

            # Test JSON report
            json_file = os.path.join(temp_dir, "report.json")
            write_json_report(sample_results, json_file)
            assert os.path.exists(json_file)


class TestMainFunctions:
    """Test cases for main module functions."""

    def test_read_log_file(self):
        """Test log file reading."""
        sample_logs = [
            '127.0.0.1 - - [25/Dec/2023:10:00:00 +0000] "GET /index.html HTTP/1.1" 200 1234 "-" "-"',
            '192.168.1.1 - - [25/Dec/2023:10:01:00 +0000] "POST /api/data HTTP/1.1" 404 567 "-" "-"',
        ]

        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            for line in sample_logs:
                f.write(line + "\n")
            temp_file = f.name

        try:
            lines = read_log_file(temp_file)
            assert len(lines) == 2
            assert lines[0] == sample_logs[0]
            assert lines[1] == sample_logs[1]
        finally:
            os.unlink(temp_file)

    def test_analyze_logs_integration(self):
        """Test full log analysis integration."""
        sample_logs = [
            '127.0.0.1 - - [25/Dec/2023:10:00:00 +0000] "GET /index.html HTTP/1.1" 200 1234 "http://example.com" "Mozilla/5.0"',
            '192.168.1.1 - - [25/Dec/2023:10:01:00 +0000] "POST /api/data HTTP/1.1" 404 567 "-" "curl/7.68.0"',
            '127.0.0.1 - - [25/Dec/2023:10:02:00 +0000] "GET /about.html HTTP/1.1" 200 2345 "http://example.com" "Mozilla/5.0"',
        ]

        results = analyze_logs(sample_logs, "combined", 10)

        assert "basic_stats" in results
        assert results["basic_stats"]["total_requests"] == 3
        assert results["basic_stats"]["unique_ips"] == 2

        assert "top_endpoints" in results
        assert len(results["top_endpoints"]) == 3

        assert "error_analysis" in results
        assert results["error_analysis"]["total_errors"] == 1


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_malformed_log_lines(self):
        """Test handling of malformed log lines."""
        malformed_logs = [
            '127.0.0.1 - - [invalid-date] "GET / HTTP/1.1" 200 1234 "-" "-"',  # Invalid date
            "invalid log line format",  # Completely invalid
            '127.0.0.1 - - [25/Dec/2023:10:00:00 +0000] "GET / HTTP/1.1" invalid 1234 "-" "-"',  # Invalid status
        ]

        parser = LogParser("combined")
        valid_entries = 0

        for line in malformed_logs:
            entry = parser.parse_line(line)
            if entry:
                valid_entries += 1

        # Should handle gracefully without crashing
        assert valid_entries == 0

    def test_large_numbers(self):
        """Test handling of large numbers in log entries."""
        large_size_log = '127.0.0.1 - - [25/Dec/2023:10:00:00 +0000] "GET /large-file.zip HTTP/1.1" 200 2147483648 "-" "-"'

        parser = LogParser("combined")
        entry = parser.parse_line(large_size_log)

        assert entry is not None
        assert entry.size == 2147483648  # 2GB

    def test_unicode_handling(self):
        """Test handling of Unicode characters in log entries."""
        unicode_log = '127.0.0.1 - - [25/Dec/2023:10:00:00 +0000] "GET /测试页面.html HTTP/1.1" 200 1234 "-" "Mozilla/5.0 (测试)"'

        parser = LogParser("combined")
        entry = parser.parse_line(unicode_log)

        assert entry is not None
        assert "测试" in entry.path
        assert "测试" in entry.user_agent

    def test_empty_analyzer_operations(self):
        """Test operations on empty analyzer."""
        analyzer = LogAnalyzer()

        # All should return empty/default values without crashing
        assert analyzer.get_basic_stats() == {}
        assert analyzer.get_top_endpoints() == []
        assert analyzer.get_top_ips() == []
        assert analyzer.get_error_analysis() == {"total_errors": 0}
        assert analyzer.get_traffic_patterns() == {}
        assert analyzer.get_performance_analysis() == {
            "message": "No response time data available"
        }
        assert analyzer.get_user_agent_analysis() == {
            "total_unique_user_agents": 0,
            "top_user_agents": [],
            "browser_distribution": {},
            "bot_traffic": {
                "total_bot_requests": 0,
                "bot_percentage": 0,
                "top_bots": {},
            },
        }


if __name__ == "__main__":
    pytest.main([__file__])

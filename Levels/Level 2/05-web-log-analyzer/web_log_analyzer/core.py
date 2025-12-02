"""Core functionality for parsing and analyzing web server logs."""

import re
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from collections import defaultdict, Counter
from dataclasses import dataclass


@dataclass
class LogEntry:
    """Represents a single log entry."""

    ip: str
    timestamp: datetime
    method: str
    path: str
    status_code: int
    size: int
    user_agent: str
    referer: str
    response_time: Optional[float] = None


class LogParser:
    """Parses Apache/Nginx access logs into structured data."""

    # Common log format patterns
    APACHE_COMMON = r'(\S+) \S+ \S+ \[([^\]]+)\] "(\S+) ([^"]+) (\S+)" (\d+) (\S+)'
    APACHE_COMBINED = r'(\S+) \S+ \S+ \[([^\]]+)\] "(\S+) ([^"]+) (\S+)" (\d+) (\S+) "([^"]*)" "([^"]*)"'
    NGINX_DEFAULT = r'(\S+) - \S+ \[([^\]]+)\] "(\S+) ([^"]+) (\S+)" (\d+) (\S+) "([^"]*)" "([^"]*)"'
    # Pattern with response time (microseconds)
    NGINX_WITH_TIME = r'(\S+) - \S+ \[([^\]]+)\] "(\S+) ([^"]+) (\S+)" (\d+) (\S+) "([^"]*)" "([^"]*)" (\S+)'

    def __init__(self, log_format: str = "combined"):
        """Initialize parser with specified log format."""
        self.log_format = log_format
        self.patterns = {
            "common": self.APACHE_COMMON,
            "combined": self.APACHE_COMBINED,
            "nginx": self.NGINX_DEFAULT,
            "nginx_time": self.NGINX_WITH_TIME,
        }
        self.pattern = self.patterns.get(log_format, self.APACHE_COMBINED)
        self.logger = logging.getLogger(__name__)

    def parse_timestamp(self, timestamp_str: str) -> datetime:
        """Parse timestamp string to datetime object."""
        try:
            # Common timestamp format: dd/MMM/yyyy:HH:mm:ss +0000
            return datetime.strptime(timestamp_str.split()[0], "%d/%b/%Y:%H:%M:%S")
        except ValueError as e:
            self.logger.warning(f"Failed to parse timestamp '{timestamp_str}': {e}")
            raise ValueError(f"Invalid timestamp: {timestamp_str}")

    def parse_size(self, size_str: str) -> int:
        """Parse size string to integer."""
        if size_str == "-":
            return 0
        try:
            return int(size_str)
        except ValueError:
            return 0

    def parse_line(self, line: str) -> Optional[LogEntry]:
        """Parse a single log line into a LogEntry object."""
        line = line.strip()
        if not line or line.startswith("#"):
            return None

        match = re.match(self.pattern, line)
        if not match:
            self.logger.warning(f"Failed to parse line: {line[:100]}...")
            return None

        try:
            groups = match.groups()

            if self.log_format == "common":
                ip, timestamp, method, path, protocol, status, size = groups
                user_agent = ""
                referer = ""
                response_time = None
            elif self.log_format == "nginx_time":
                (
                    ip,
                    timestamp,
                    method,
                    path,
                    protocol,
                    status,
                    size,
                    referer,
                    user_agent,
                    time_str,
                ) = groups
                response_time = (
                    float(time_str) / 1000000 if time_str != "-" else None
                )  # Convert from microseconds
            else:
                (
                    ip,
                    timestamp,
                    method,
                    path,
                    protocol,
                    status,
                    size,
                    referer,
                    user_agent,
                ) = groups
                response_time = None

            return LogEntry(
                ip=ip,
                timestamp=self.parse_timestamp(timestamp),
                method=method,
                path=path,
                status_code=int(status),
                size=self.parse_size(size),
                user_agent=user_agent,
                referer=referer,
                response_time=response_time,
            )
        except (ValueError, IndexError) as e:
            self.logger.warning(f"Error parsing line: {e}")
            return None


class LogAnalyzer:
    """Analyzes parsed log entries and generates statistics."""

    def __init__(self):
        """Initialize analyzer."""
        self.logger = logging.getLogger(__name__)
        self.entries: List[LogEntry] = []

    def add_entries(self, entries: List[LogEntry]) -> None:
        """Add log entries for analysis."""
        self.entries.extend(entries)
        self.logger.info(f"Added {len(entries)} log entries")

    def get_basic_stats(self) -> Dict[str, Any]:
        """Get basic statistics about the log entries."""
        if not self.entries:
            return {}

        total_requests = len(self.entries)
        status_counts = Counter(entry.status_code for entry in self.entries)
        method_counts = Counter(entry.method for entry in self.entries)
        total_bytes = sum(entry.size for entry in self.entries)

        # Calculate time range
        timestamps = [entry.timestamp for entry in self.entries]
        start_time = min(timestamps)
        end_time = max(timestamps)

        return {
            "total_requests": total_requests,
            "unique_ips": len(set(entry.ip for entry in self.entries)),
            "time_range": {
                "start": start_time.isoformat(),
                "end": end_time.isoformat(),
                "duration_hours": (end_time - start_time).total_seconds() / 3600,
            },
            "status_distribution": dict(status_counts.most_common()),
            "method_distribution": dict(method_counts.most_common()),
            "total_bytes_served": total_bytes,
            "avg_bytes_per_request": (
                total_bytes / total_requests if total_requests > 0 else 0
            ),
        }

    def get_top_endpoints(self, limit: int = 10) -> List[Tuple[str, int]]:
        """Get most frequently accessed endpoints."""
        endpoint_counts = Counter(entry.path for entry in self.entries)
        return endpoint_counts.most_common(limit)

    def get_top_ips(self, limit: int = 10) -> List[Tuple[str, int]]:
        """Get IPs with most requests."""
        ip_counts = Counter(entry.ip for entry in self.entries)
        return ip_counts.most_common(limit)

    def get_error_analysis(self) -> Dict[str, Any]:
        """Analyze error patterns (4xx and 5xx status codes)."""
        error_entries = [entry for entry in self.entries if entry.status_code >= 400]

        if not error_entries:
            return {"total_errors": 0}

        status_counts = Counter(entry.status_code for entry in error_entries)
        error_endpoints = Counter(entry.path for entry in error_entries)
        error_ips = Counter(entry.ip for entry in error_entries)

        # Find 404s specifically
        not_found_entries = [
            entry for entry in error_entries if entry.status_code == 404
        ]
        not_found_paths = Counter(entry.path for entry in not_found_entries)

        return {
            "total_errors": len(error_entries),
            "error_rate": len(error_entries) / len(self.entries) * 100,
            "status_distribution": dict(status_counts.most_common()),
            "top_error_endpoints": error_endpoints.most_common(10),
            "top_error_ips": error_ips.most_common(10),
            "not_found_analysis": {
                "total_404s": len(not_found_entries),
                "top_missing_paths": not_found_paths.most_common(10),
            },
        }

    def get_traffic_patterns(self) -> Dict[str, Any]:
        """Analyze traffic patterns over time."""
        if not self.entries:
            return {}

        # Group by hour
        hourly_requests = defaultdict(int)
        for entry in self.entries:
            hour = entry.timestamp.hour
            hourly_requests[hour] += 1

        # Group by day of week
        daily_requests = defaultdict(int)
        for entry in self.entries:
            day = entry.timestamp.strftime("%A")
            daily_requests[day] += 1

        return {
            "hourly_distribution": dict(hourly_requests),
            "daily_distribution": dict(daily_requests),
            "peak_hour": (
                max(hourly_requests.items(), key=lambda x: x[1])
                if hourly_requests
                else None
            ),
            "peak_day": (
                max(daily_requests.items(), key=lambda x: x[1])
                if daily_requests
                else None
            ),
        }

    def get_performance_analysis(self) -> Dict[str, Any]:
        """Analyze performance metrics if response times are available."""
        entries_with_time = [
            entry for entry in self.entries if entry.response_time is not None
        ]

        if not entries_with_time:
            return {"message": "No response time data available"}

        response_times = [entry.response_time for entry in entries_with_time]

        # Find slow requests
        slow_threshold = 1.0  # 1 second
        slow_requests = [
            entry for entry in entries_with_time if entry.response_time > slow_threshold
        ]

        return {
            "total_requests_with_time": len(entries_with_time),
            "avg_response_time": sum(response_times) / len(response_times),
            "min_response_time": min(response_times),
            "max_response_time": max(response_times),
            "slow_requests": {
                "threshold_seconds": slow_threshold,
                "count": len(slow_requests),
                "percentage": len(slow_requests) / len(entries_with_time) * 100,
                "slowest_endpoints": Counter(
                    entry.path for entry in slow_requests
                ).most_common(10),
            },
        }

    def get_user_agent_analysis(self) -> Dict[str, Any]:
        """Analyze user agent patterns."""
        user_agents = Counter(
            entry.user_agent for entry in self.entries if entry.user_agent
        )

        # Simple browser detection
        browsers = defaultdict(int)
        bots = defaultdict(int)

        for ua, count in user_agents.items():
            ua_lower = ua.lower()
            if any(bot in ua_lower for bot in ["bot", "crawler", "spider", "scraper"]):
                bots[ua] += count
            elif "chrome" in ua_lower:
                browsers["Chrome"] += count
            elif "firefox" in ua_lower:
                browsers["Firefox"] += count
            elif "safari" in ua_lower and "chrome" not in ua_lower:
                browsers["Safari"] += count
            elif "edge" in ua_lower:
                browsers["Edge"] += count
            else:
                browsers["Other"] += count

        return {
            "total_unique_user_agents": len(user_agents),
            "top_user_agents": user_agents.most_common(10),
            "browser_distribution": dict(browsers),
            "bot_traffic": {
                "total_bot_requests": sum(bots.values()),
                "bot_percentage": (
                    sum(bots.values()) / len(self.entries) * 100 if self.entries else 0
                ),
                "top_bots": dict(Counter(bots).most_common(5)),
            },
        }

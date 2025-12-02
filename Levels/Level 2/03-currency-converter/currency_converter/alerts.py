"""
Currency rate change alerts and monitoring functionality.
"""

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class RateAlert:
    """Represents a currency rate change alert."""

    def __init__(self, currency_pair: str, threshold_percent: float,
                 current_rate: float, alert_type: str = "change"):
        """
        Initialize a rate alert.

        Args:
            currency_pair: Currency pair (e.g., "USD/EUR")
            threshold_percent: Threshold percentage for alert
            current_rate: Current exchange rate
            alert_type: Type of alert ("change", "above", "below")
        """
        self.currency_pair = currency_pair
        self.threshold_percent = threshold_percent
        self.current_rate = current_rate
        self.alert_type = alert_type
        self.created_at = datetime.now()
        self.triggered = False
        self.triggered_at: Optional[datetime] = None

    def check_rate(self, new_rate: float) -> bool:
        """
        Check if the alert should be triggered.

        Args:
            new_rate: New exchange rate to check

        Returns:
            True if alert should be triggered
        """
        if self.triggered:
            return False

        rate_change = abs(new_rate - self.current_rate) / self.current_rate * 100

        if self.alert_type == "change":
            should_trigger = rate_change >= self.threshold_percent
        elif self.alert_type == "above":
            should_trigger = new_rate > self.current_rate * (1 + self.threshold_percent / 100)
        elif self.alert_type == "below":
            should_trigger = new_rate < self.current_rate * (1 - self.threshold_percent / 100)
        else:
            should_trigger = False

        if should_trigger:
            self.triggered = True
            self.triggered_at = datetime.now()
            logger.info(f"Alert triggered for {self.currency_pair}: {rate_change:.2f}% change")

        return should_trigger

    def to_dict(self) -> Dict:
        """Convert alert to dictionary for serialization."""
        return {
            "currency_pair": self.currency_pair,
            "threshold_percent": self.threshold_percent,
            "current_rate": self.current_rate,
            "alert_type": self.alert_type,
            "created_at": self.created_at.isoformat(),
            "triggered": self.triggered,
            "triggered_at": self.triggered_at.isoformat() if self.triggered_at else None
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'RateAlert':
        """Create alert from dictionary."""
        alert = cls(
            data["currency_pair"],
            data["threshold_percent"],
            data["current_rate"],
            data["alert_type"]
        )
        alert.created_at = datetime.fromisoformat(data["created_at"])
        alert.triggered = data["triggered"]
        if data["triggered_at"]:
            alert.triggered_at = datetime.fromisoformat(data["triggered_at"])
        return alert


class AlertManager:
    """Manages currency rate change alerts."""

    def __init__(self, alerts_file: str = "rate_alerts.json"):
        """
        Initialize the alert manager.

        Args:
            alerts_file: Path to file for storing alerts
        """
        self.alerts_file = Path(alerts_file)
        self.alerts: List[RateAlert] = []
        self._load_alerts()

    def _load_alerts(self) -> None:
        """Load alerts from file."""
        try:
            if self.alerts_file.exists():
                with open(self.alerts_file, 'r') as f:
                    data = json.load(f)
                    self.alerts = [RateAlert.from_dict(alert_data) for alert_data in data]
                    logger.info(f"Loaded {len(self.alerts)} alerts")
        except Exception as e:
            logger.warning(f"Failed to load alerts: {e}")
            self.alerts = []

    def _save_alerts(self) -> None:
        """Save alerts to file."""
        try:
            data = [alert.to_dict() for alert in self.alerts]
            with open(self.alerts_file, 'w') as f:
                json.dump(data, f, indent=2)
            logger.info("Alerts saved to file")
        except Exception as e:
            logger.error(f"Failed to save alerts: {e}")

    def add_alert(self, currency_pair: str, threshold_percent: float,
                  current_rate: float, alert_type: str = "change") -> str:
        """
        Add a new rate alert.

        Args:
            currency_pair: Currency pair (e.g., "USD/EUR")
            threshold_percent: Threshold percentage for alert
            current_rate: Current exchange rate
            alert_type: Type of alert ("change", "above", "below")

        Returns:
            Alert ID
        """
        alert = RateAlert(currency_pair, threshold_percent, current_rate, alert_type)
        self.alerts.append(alert)
        self._save_alerts()

        logger.info(f"Added alert for {currency_pair} with {threshold_percent}% threshold")
        return f"alert_{len(self.alerts) - 1}"

    def check_alerts(self, rates: Dict[str, float]) -> List[Tuple[RateAlert, float]]:
        """
        Check all alerts against current rates.

        Args:
            rates: Current exchange rates

        Returns:
            List of triggered alerts with new rates
        """
        triggered_alerts = []

        for alert in self.alerts:
            if alert.triggered:
                continue

            # Parse currency pair
            from_curr, to_curr = alert.currency_pair.split('/')

            # Calculate current rate
            if from_curr == "USD":
                current_rate = rates.get(to_curr, 1.0)
            elif to_curr == "USD":
                current_rate = 1.0 / rates.get(from_curr, 1.0)
            else:
                from_rate = rates.get(from_curr, 1.0)
                to_rate = rates.get(to_curr, 1.0)
                current_rate = to_rate / from_rate

            if alert.check_rate(current_rate):
                triggered_alerts.append((alert, current_rate))

        if triggered_alerts:
            self._save_alerts()

        return triggered_alerts

    def list_alerts(self) -> List[Dict]:
        """
        List all alerts.

        Returns:
            List of alert information
        """
        return [
            {
                "id": f"alert_{i}",
                "currency_pair": alert.currency_pair,
                "threshold_percent": alert.threshold_percent,
                "current_rate": alert.current_rate,
                "alert_type": alert.alert_type,
                "created_at": alert.created_at.isoformat(),
                "triggered": alert.triggered,
                "triggered_at": alert.triggered_at.isoformat() if alert.triggered_at else None
            }
            for i, alert in enumerate(self.alerts)
        ]

    def remove_alert(self, alert_id: str) -> bool:
        """
        Remove an alert by ID.

        Args:
            alert_id: Alert ID to remove

        Returns:
            True if alert was removed, False if not found
        """
        try:
            index = int(alert_id.replace("alert_", ""))
            if 0 <= index < len(self.alerts):
                removed_alert = self.alerts.pop(index)
                self._save_alerts()
                logger.info(f"Removed alert for {removed_alert.currency_pair}")
                return True
        except (ValueError, IndexError):
            pass

        return False

    def clear_triggered_alerts(self) -> int:
        """
        Clear all triggered alerts.

        Returns:
            Number of alerts cleared
        """
        initial_count = len(self.alerts)
        self.alerts = [alert for alert in self.alerts if not alert.triggered]
        cleared_count = initial_count - len(self.alerts)

        if cleared_count > 0:
            self._save_alerts()
            logger.info(f"Cleared {cleared_count} triggered alerts")

        return cleared_count

    def get_alert_stats(self) -> Dict:
        """
        Get alert statistics.

        Returns:
            Dictionary with alert statistics
        """
        total_alerts = len(self.alerts)
        triggered_alerts = sum(1 for alert in self.alerts if alert.triggered)
        active_alerts = total_alerts - triggered_alerts

        return {
            "total_alerts": total_alerts,
            "active_alerts": active_alerts,
            "triggered_alerts": triggered_alerts,
            "trigger_rate": (triggered_alerts / total_alerts * 100) if total_alerts > 0 else 0
        }

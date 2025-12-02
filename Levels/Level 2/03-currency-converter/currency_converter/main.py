"""
Command-line interface for the currency converter.
"""

import argparse
import logging
import sys
from pathlib import Path
from typing import List, Optional

from .core import CurrencyConverter
from .alerts import AlertManager


def setup_logging(verbose: bool = False) -> None:
    """Setup logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


def convert_currency(args) -> None:
    """Handle single currency conversion."""
    converter = CurrencyConverter()

    try:
        amount, timestamp = converter.convert(
            args.amount,
            args.from_currency,
            args.to_currency
        )

        # Check if in offline mode
        offline_warning = ""
        if converter.is_offline_mode():
            offline_warning = " (OFFLINE MODE - using cached data)"

        print(f"\n💰 Currency Conversion Result:")
        print(f"   {args.amount} {args.from_currency.upper()} = {amount} {args.to_currency.upper()}")
        print(f"   Last updated: {timestamp}{offline_warning}")

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


def convert_historical(args) -> None:
    """Handle historical currency conversion."""
    converter = CurrencyConverter()

    try:
        amount, date = converter.convert_historical(
            args.amount,
            args.from_currency,
            args.to_currency,
            args.date
        )

        print(f"\n📅 Historical Currency Conversion Result:")
        print(f"   {args.amount} {args.from_currency.upper()} = {amount} {args.to_currency.upper()}")
        print(f"   Date: {date}")

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


def batch_convert(args) -> None:
    """Handle batch conversion from CSV."""
    converter = CurrencyConverter()

    try:
        converter.batch_convert_csv(
            args.input_file,
            args.output_file,
            args.amount_column,
            args.from_column,
            args.to_column
        )

        print(f"\n✅ Batch conversion completed!")
        print(f"   Input: {args.input_file}")
        print(f"   Output: {args.output_file}")

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


def list_currencies(args) -> None:
    """List supported currencies."""
    converter = CurrencyConverter()

    try:
        currencies = converter.get_supported_currencies()

        print(f"\n🌍 Supported Currencies ({len(currencies)}):")
        for i, currency in enumerate(currencies, 1):
            print(f"   {i:2d}. {currency}")

        if converter.is_offline_mode():
            print(f"\n⚠️  Note: Currently in offline mode (using cached data)")

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


def refresh_rates(args) -> None:
    """Force refresh exchange rates."""
    converter = CurrencyConverter()

    try:
        if converter.fetch_live_rates():
            print("✅ Exchange rates refreshed successfully!")
        else:
            print("❌ Failed to refresh exchange rates", file=sys.stderr)
            sys.exit(1)

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


def create_sample_csv(args) -> None:
    """Create a sample CSV file for batch conversion."""
    import pandas as pd

    sample_data = {
        'amount': [100, 250, 50, 1000],
        'from_currency': ['USD', 'EUR', 'GBP', 'JPY'],
        'to_currency': ['EUR', 'USD', 'CAD', 'USD']
    }

    df = pd.DataFrame(sample_data)
    df.to_csv(args.output_file, index=False)

    print(f"✅ Sample CSV created: {args.output_file}")
    print("\nSample data:")
    print(df.to_string(index=False))


def add_alert(args) -> None:
    """Add a currency rate alert."""
    converter = CurrencyConverter()
    alert_manager = AlertManager()

    try:
        # Get current rate for the currency pair
        from_curr, to_curr = args.currency_pair.split('/')
        rates = converter.get_rates()

        if from_curr == "USD":
            current_rate = rates.get(to_curr, 1.0)
        elif to_curr == "USD":
            current_rate = 1.0 / rates.get(from_curr, 1.0)
        else:
            from_rate = rates.get(from_curr, 1.0)
            to_rate = rates.get(to_curr, 1.0)
            current_rate = to_rate / from_rate

        alert_id = alert_manager.add_alert(
            args.currency_pair,
            args.threshold,
            current_rate,
            args.type
        )

        print(f"✅ Alert added successfully!")
        print(f"   ID: {alert_id}")
        print(f"   Pair: {args.currency_pair}")
        print(f"   Threshold: {args.threshold}%")
        print(f"   Type: {args.type}")
        print(f"   Current Rate: {current_rate:.6f}")

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


def list_alerts(args) -> None:
    """List all currency rate alerts."""
    alert_manager = AlertManager()

    try:
        alerts = alert_manager.list_alerts()

        if not alerts:
            print("\n📋 No alerts configured")
            return

        print(f"\n🚨 Currency Rate Alerts ({len(alerts)}):")
        print("=" * 80)

        for alert in alerts:
            status = "🔴 TRIGGERED" if alert["triggered"] else "🟢 Active"
            print(f"ID: {alert['id']}")
            print(f"Pair: {alert['currency_pair']}")
            print(f"Threshold: {alert['threshold_percent']}%")
            print(f"Type: {alert['alert_type']}")
            print(f"Current Rate: {alert['current_rate']:.6f}")
            print(f"Status: {status}")
            print(f"Created: {alert['created_at']}")
            if alert["triggered_at"]:
                print(f"Triggered: {alert['triggered_at']}")
            print("-" * 80)

        # Show statistics
        stats = alert_manager.get_alert_stats()
        print(f"\n📊 Alert Statistics:")
        print(f"   Total: {stats['total_alerts']}")
        print(f"   Active: {stats['active_alerts']}")
        print(f"   Triggered: {stats['triggered_alerts']}")
        print(f"   Trigger Rate: {stats['trigger_rate']:.1f}%")

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


def check_alerts(args) -> None:
    """Check all currency rate alerts."""
    converter = CurrencyConverter()
    alert_manager = AlertManager()

    try:
        rates = converter.get_rates()
        triggered_alerts = alert_manager.check_alerts(rates)

        if not triggered_alerts:
            print("\n✅ No alerts triggered")
            return

        print(f"\n🚨 {len(triggered_alerts)} Alert(s) Triggered!")
        print("=" * 60)

        for alert, new_rate in triggered_alerts:
            rate_change = abs(new_rate - alert.current_rate) / alert.current_rate * 100
            print(f"Pair: {alert.currency_pair}")
            print(f"Old Rate: {alert.current_rate:.6f}")
            print(f"New Rate: {new_rate:.6f}")
            print(f"Change: {rate_change:.2f}%")
            print(f"Triggered: {alert.triggered_at}")
            print("-" * 60)

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


def remove_alert(args) -> None:
    """Remove a currency rate alert."""
    alert_manager = AlertManager()

    try:
        if alert_manager.remove_alert(args.alert_id):
            print(f"✅ Alert {args.alert_id} removed successfully")
        else:
            print(f"❌ Alert {args.alert_id} not found", file=sys.stderr)
            sys.exit(1)

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


def clear_alerts(args) -> None:
    """Clear all triggered alerts."""
    alert_manager = AlertManager()

    try:
        cleared_count = alert_manager.clear_triggered_alerts()
        print(f"✅ Cleared {cleared_count} triggered alerts")

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


def main(argv: Optional[List[str]] = None) -> None:
    """Main entry point for the currency converter CLI."""
    parser = argparse.ArgumentParser(
        description="Professional Currency Converter with Live Exchange Rates",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Convert 100 USD to EUR
  python -m currency_converter convert 100 USD EUR

  # Convert with historical rates
  python -m currency_converter historical 100 USD EUR --date 2023-01-01

  # Batch convert from CSV
  python -m currency_converter batch input.csv output.csv

  # List supported currencies
  python -m currency_converter list

  # Refresh exchange rates
  python -m currency_converter refresh

  # Add currency rate alert
  python -m currency_converter alerts add USD/EUR 5.0 --type change

  # List all alerts
  python -m currency_converter alerts list

  # Check for triggered alerts
  python -m currency_converter alerts check
        """
    )

    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Convert command
    convert_parser = subparsers.add_parser('convert', help='Convert currency')
    convert_parser.add_argument('amount', type=float, help='Amount to convert')
    convert_parser.add_argument('from_currency', help='Source currency code')
    convert_parser.add_argument('to_currency', help='Target currency code')

    # Historical convert command
    historical_parser = subparsers.add_parser('historical', help='Convert with historical rates')
    historical_parser.add_argument('amount', type=float, help='Amount to convert')
    historical_parser.add_argument('from_currency', help='Source currency code')
    historical_parser.add_argument('to_currency', help='Target currency code')
    historical_parser.add_argument('--date', required=True, help='Date in YYYY-MM-DD format')

    # Batch convert command
    batch_parser = subparsers.add_parser('batch', help='Batch convert from CSV')
    batch_parser.add_argument('input_file', help='Input CSV file path')
    batch_parser.add_argument('output_file', help='Output CSV file path')
    batch_parser.add_argument('--amount-column', default='amount', help='Amount column name')
    batch_parser.add_argument('--from-column', default='from_currency', help='From currency column name')
    batch_parser.add_argument('--to-column', default='to_currency', help='To currency column name')

    # List currencies command
    subparsers.add_parser('list', help='List supported currencies')

    # Refresh rates command
    subparsers.add_parser('refresh', help='Refresh exchange rates from API')

    # Create sample CSV command
    sample_parser = subparsers.add_parser('sample', help='Create sample CSV for batch conversion')
    sample_parser.add_argument('output_file', help='Output CSV file path')

    # Alert commands
    alert_subparsers = subparsers.add_parser('alerts', help='Currency rate alerts').add_subparsers(dest='alert_command')

    # Add alert command
    add_alert_parser = alert_subparsers.add_parser('add', help='Add a currency rate alert')
    add_alert_parser.add_argument('currency_pair', help='Currency pair (e.g., USD/EUR)')
    add_alert_parser.add_argument('threshold', type=float, help='Threshold percentage')
    add_alert_parser.add_argument('--type', choices=['change', 'above', 'below'],
                                 default='change', help='Alert type')

    # List alerts command
    alert_subparsers.add_parser('list', help='List all alerts')

    # Check alerts command
    alert_subparsers.add_parser('check', help='Check all alerts')

    # Remove alert command
    remove_alert_parser = alert_subparsers.add_parser('remove', help='Remove an alert')
    remove_alert_parser.add_argument('alert_id', help='Alert ID to remove')

    # Clear alerts command
    alert_subparsers.add_parser('clear', help='Clear all triggered alerts')

    args = parser.parse_args(argv)

    # Setup logging
    setup_logging(args.verbose)

    # Handle commands
    if args.command == 'convert':
        convert_currency(args)
    elif args.command == 'historical':
        convert_historical(args)
    elif args.command == 'batch':
        batch_convert(args)
    elif args.command == 'list':
        list_currencies(args)
    elif args.command == 'refresh':
        refresh_rates(args)
    elif args.command == 'sample':
        create_sample_csv(args)
    elif args.command == 'alerts':
        if args.alert_command == 'add':
            add_alert(args)
        elif args.alert_command == 'list':
            list_alerts(args)
        elif args.alert_command == 'check':
            check_alerts(args)
        elif args.alert_command == 'remove':
            remove_alert(args)
        elif args.alert_command == 'clear':
            clear_alerts(args)
        else:
            parser.print_help()
            sys.exit(1)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()

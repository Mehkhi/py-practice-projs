#!/usr/bin/env python3
"""CLI Address Autocomplete main entry point."""

import argparse
import logging
import sys
from .core import AddressAutocomplete


def main():
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    parser = argparse.ArgumentParser(description="CLI Address Autocomplete")
    parser.add_argument("query", help="Address query to autocomplete")
    parser.add_argument("--limit", type=int, default=10, help="Maximum number of results")
    parser.add_argument("--page", type=int, default=1, help="Page number for pagination")
    parser.add_argument("--dataset", default="sample_addresses.csv", help="Path to address dataset CSV")

    args = parser.parse_args()

    try:
        autocomplete = AddressAutocomplete(args.dataset)
        results = autocomplete.search(args.query, limit=args.limit, page=args.page)
        for addr in results:
            print(addr)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

"""Command line interface for b3ajustes."""

import argparse
import csv
import sys
import codecs
import json
import time
from datetime import datetime

from .scraper import (
    scrape_ajustes,
    is_business_day,
    get_next_business_day,
    get_previous_business_day,
)


def main() -> int:
    """Execute the main CLI program."""
    parser = argparse.ArgumentParser(
        description="Scrape BMF Bovespa settlement prices for a given date."
    )
    parser.add_argument("date", help="Starting date in DD/MM/YYYY format")
    parser.add_argument("-f", "--file", help="Output CSV file path")
    parser.add_argument(
        "-d",
        "--days",
        type=int,
        help="Number of business days to process (default: 1)",
        default=1,
    )
    parser.add_argument(
        "--delay",
        type=float,
        help="Delay between requests in seconds (default: 1.0)",
        default=1.0,
    )
    parser.add_argument(
        "-b",
        "--backward",
        action="store_true",
        help="Process dates backward from the start date (default: forward)",
    )
    parser.add_argument(
        "-j",
        "--json",
        action="store_true",
        help="Output JSON to stdout (default: off)",
    )
    args = parser.parse_args()

    # Validate date format and get datetime object
    try:
        start_date = datetime.strptime(args.date, "%d/%m/%Y")
    except ValueError:
        print("Error: Date must be in DD/MM/YYYY format", file=sys.stderr)
        return 1

    # Initialize data collection
    all_data = []
    current_date = start_date
    days_processed = 0

    # Choose the appropriate date function based on direction
    get_next_date = (
        get_previous_business_day if args.backward else get_next_business_day
    )

    while days_processed < args.days:
        if is_business_day(current_date):
            date_str = current_date.strftime("%d/%m/%Y")
            print(f"Processing date: {date_str}", file=sys.stderr)

            # Get the data
            data = scrape_ajustes(date_str)
            if data:
                # Add date to each row
                for row in data:
                    row["Data"] = date_str
                all_data.extend(data)
                days_processed += 1

            # Rate limiting
            if days_processed < args.days:
                time.sleep(args.delay)

        current_date = get_next_date(current_date)

    if not all_data:
        print("No data was found for any of the requested dates.", file=sys.stderr)
        return 1

    # Output JSON if requested
    if args.json:
        # Set stdout to use UTF-8
        sys.stdout = codecs.getwriter("utf-8")(sys.stdout.buffer)
        # Print JSON to stdout
        print(json.dumps(all_data, indent=2, ensure_ascii=False))

    # If a file path is provided, save as CSV
    if args.file:
        try:
            # Ensure "Data" and "Ticker" are the first columns
            all_keys = list(all_data[0].keys())
            fieldnames = ["Data", "Ticker"] + [
                field for field in all_keys if field not in ("Data", "Ticker")
            ]
            with open(args.file, "w", newline="", encoding="iso-8859-1") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=";")
                writer.writeheader()
                writer.writerows(all_data)
            print(f"\nData saved to CSV file: {args.file}", file=sys.stderr)
        except IOError as e:
            print(f"Error saving to CSV file: {e}", file=sys.stderr)
            return 1

    return 0

"""Example: programmatically use b3ajustes.scraper.scrape_ajustes

This small script shows how to call the library from Python code, save CSV
(using the same CSV settings as the CLI) and/or print JSON.

Usage:
    python examples/run_programmatic.py 31/10/2025 --csv output.csv --json

This file is optional — it demonstrates the public function API for consumers
who don't want to use the CLI.
"""

import sys
import csv
import json
from pathlib import Path
from datetime import datetime

from b3ajustes.scraper import scrape_ajustes


def main(argv=None) -> int:
    argv = argv or sys.argv[1:]
    if not argv:
        print("Usage: run_programmatic.py <date (DD/MM/YYYY)> [--csv OUT] [--json]")
        return 1

    # Minimal arg parsing
    date = argv[0]
    out_csv = None
    do_json = False
    if "--csv" in argv:
        idx = argv.index("--csv")
        if idx + 1 < len(argv):
            out_csv = argv[idx + 1]
    if "--json" in argv:
        do_json = True

    # Validate date format
    try:
        datetime.strptime(date, "%d/%m/%Y")
    except ValueError:
        print("Error: date must be in DD/MM/YYYY format")
        return 2

    # Call the scraper
    data = scrape_ajustes(date)
    if not data:
        print("No data returned by scraper")
        return 3

    # Add Data field (same as CLI does)
    for row in data:
        row["Data"] = date

    # Print JSON if requested
    if do_json:
        print(json.dumps(data, ensure_ascii=False, indent=2))

    # Save CSV if requested
    if out_csv:
        Path(out_csv).parent.mkdir(parents=True, exist_ok=True)
        # Ensure Data and Ticker are first columns when writing
        keys = list(data[0].keys())
        fieldnames = ["Data", "Ticker"] + [
            k for k in keys if k not in ("Data", "Ticker")
        ]
        with open(out_csv, "w", encoding="iso-8859-1", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=";")
            writer.writeheader()
            writer.writerows(data)
        print(f"Saved CSV to {out_csv}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

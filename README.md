# B3 Ajustes

A small Python package that fetches "ajustes do pregão" from BMF Bovespa and
outputs JSON and/or CSV.

## Features

- Scrapes settlement/adjustment tables for a given date.
- Handles server encoding (ISO-8859-1) and produces CSV compatible with Excel
  (ISO-8859-1 + semicolon separator).
- Fills grouped empty `Mercadoria` values from the last non-empty value.
- Adds a generated `Ticker` field (prefix of `Mercadoria` before `-` +
  `Vencimento`, spaces removed).
- Supports multi-day business-day runs, forward or backward, with rate limiting.
- Project is fully compliant with `uv` and `uvx` tools

## Quickstart

1. Install the package locally for development using uv:

```sh
uv tool install -e .
```

2. Run the command-line tool `b3ajustes`:

```sh
# Single day, save CSV
b3ajustes 31/10/2025 -f ajuste_2025-10-31.csv

# Multiple business days (forward), print JSON to stdout
b3ajustes 01/10/2025 -d 5 -j

# Multiple business days (backward), save CSV
b3ajustes 03/11/2025 -d 10 -b -f ajuste_2025-11.csv
```

## Installation

You can install the project locally (editable) for development or normally using
`uv`:

```sh
# Editable / development install
uv tool install -e .

# Normal install
uv tool install .
```

The commands above will install the `b3ajustes` console script into the active
tool environment so you can run it directly from your shell.

## CLI usage and options

Usage summary:

```text
b3ajustes <date> [-f FILE] [-d DAYS] [--delay SECONDS] [-b] [-j]
```

Options:

- date (positional): Starting date in DD/MM/YYYY format.
- -f, --file: Output CSV file path. When present data is written as CSV
  (encoding=ISO-8859-1, delimiter=';').
- -d, --days: Number of business days to process (default: 1).
- --delay: Delay between requests in seconds (default: 1.0).
- -b, --backward: Process dates backward from the start date (default: forward).
- -j, --json: Print JSON to stdout (UTF-8) instead of or in addition to CSV.

Example:

```sh
b3ajustes 15/09/2025 -d 3 --delay 0.5 -f ajuste_sep.csv
```

## CSV / JSON specifics

- CSVs are written with `encoding=iso-8859-1` and `;` as delimiter to open
  correctly in Excel on Portuguese Windows locales.
- JSON printed to stdout is encoded as UTF-8 and `ensure_ascii=False` is used to
  preserve Unicode characters.

## Examples

1. Run the provided programmatic example script (from the repository root):

```powershell
python .\\examples\\run_programmatic.py 31/10/2025 --csv output.csv --json
```

This script demonstrates how to call the scraper from Python and save the
results to CSV or print JSON.

2. Minimal programmatic usage (import in your code):

```python
from b3ajustes.scraper import scrape_ajustes

# scrape for a single date
rows = scrape_ajustes("31/10/2025")
if rows:
    # each row is a dict; add the Data field if you want the same layout as CLI
    for r in rows:
        r["Data"] = "31/10/2025"
    # Now write CSV, inspect, or further process
```

## Notes

- `Ticker` is generated from the `Mercadoria` column (text before the first `-`)
  concatenated with `Vencimento`, with spaces removed.
- Empty `Mercadoria` cells in grouped rows are filled with the last non-empty
  `Mercadoria` from the same table.
- Weekends (Sat/Sun) are skipped when counting business days.

## PowerShell UTF-8 tip

If your PowerShell does not display UTF-8 correctly, set the output encoding:

```powershell
$OutputEncoding = [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
```

## Dependencies

- Python 3.8+
- httpx, beautifulsoup4, lxml (installed via requirements or the package)

---

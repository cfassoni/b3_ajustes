A small scraper that fetches "ajustes do pregão" from BMF Bovespa and outputs JSON and/or CSV.

Features
- Scrapes settlement/adjustment tables for a given date.
- Handles server encoding (ISO-8859-1) and produces CSV compatible with Excel (ISO-8859-1 + semicolon separator).
- Fills grouped empty "Mercadoria" values from the last non-empty value.
- Adds a generated "Ticker" field (prefix of `Mercadoria` before `-` + `Vencimento`, spaces removed).
- Supports multi-day business-day runs, forward or backward, with rate limiting.

Dependencies
- Python 3.8+
- See `requirements.txt` for packages. Install with:

```powershell
pip install -r requirements.txt
```

Usage

Basic single-day (CSV only):

```powershell
python scraper.py 31/10/2025 -f ajuste_2025-10-31.csv
```

Multiple business days (forward):

```powershell
python scraper.py 01/10/2025 -d 5 -f ajuste_2025-10.csv
```

Multiple business days (backward):

```powershell
python scraper.py 03/11/2025 -d 10 -b -f ajuste_2025-11.csv
```

JSON output
- By default JSON output is off. Use `-j` or `--json` to print JSON to stdout (UTF-8).

```powershell
python scraper.py 03/11/2025 -d 3 -j
```

Rate limiting
- Use `--delay` to set seconds between requests (default 1.0). Keep this reasonable to avoid overloading the site.

CSV encoding and separator
- CSV files are written with `encoding=iso-8859-1` and `;` delimiter to open properly in Excel on Windows (Portuguese locales).

Notes
- `Ticker` is created from `Mercadoria` (text before the first `-`) concatenated with `Vencimento` with spaces removed. If `Mercadoria` is empty on a given row, the last known non-empty `Mercadoria` in that table is used.
- The scraper respects weekends (skips Saturdays and Sundays when counting business days).
- If you want the terminal to display UTF-8 correctly in PowerShell, you can set:

```powershell
$OutputEncoding = [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
```

License / attribution
- No license set. Use as you wish.


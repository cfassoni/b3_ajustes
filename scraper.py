import httpx
from bs4 import BeautifulSoup
import json
from datetime import datetime, timedelta


def is_business_day(date):
    """Check if the given date is a business day (Monday to Friday)."""
    return date.weekday() < 5


def get_next_business_day(date):
    """Get the next business day from the given date."""
    next_day = date + timedelta(days=1)
    while not is_business_day(next_day):
        next_day += timedelta(days=1)
    return next_day


def get_previous_business_day(date):
    """Get the previous business day from the given date."""
    prev_day = date - timedelta(days=1)
    while not is_business_day(prev_day):
        prev_day -= timedelta(days=1)
    return prev_day


def scrape_ajustes(date_str: str):
    """
    Scrapes the BMF Bovespa website for settlement prices for a given date.

    Args:
        date_str: The date in the format "dd/mm/yyyy".

    Returns:
        list: List of dictionaries containing the scraped data, or None if no data is found.
    """
    url = "https://www2.bmf.com.br/pages/portal/bmfbovespa/lumis/lum-ajustes-do-pregao-ptBR.asp"
    headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "accept-language": "pt-BR,pt;q=0.6",
        "cache-control": "max-age=0",
        "content-type": "application/x-www-form-urlencoded",
        "origin": "https://www2.bmf.com.br",
        # 'priority': 'u=0, i',
        # 'referer': 'https://www2.bmf.com.br/pages/portal/bmfbovespa/lumis/lum-ajustes-do-pregao-ptBR.asp',
        # 'sec-ch-ua': '"Chromium";v="142", "Brave";v="142", "Not_A Brand";v="99"',
        # 'sec-ch-ua-mobile': '?0',
        # 'sec-ch-ua-platform': '"Windows"',
        # 'sec-fetch-dest': 'iframe',
        # 'sec-fetch-mode': 'navigate',
        # 'sec-fetch-site': 'same-origin',
        # 'sec-fetch-storage-access': 'none',
        # 'sec-fetch-user': '?1',
        # 'sec-gpc': '1',
        # 'upgrade-insecure-requests': '1',
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
    }
    data = {"dData1": date_str}

    try:
        with httpx.Client() as client:
            response = client.post(url, headers=headers, data=data)
            response.raise_for_status()
            # Get raw bytes from the response. The server sends iso-8859-1
            # encoded content; pass bytes to BeautifulSoup and provide
            # from_encoding so BS can correctly decode it. This avoids the
            # UserWarning that happens when you pass a Unicode string and
            # also provide from_encoding.
            raw = response.content

        soup = BeautifulSoup(raw, "lxml", from_encoding="iso-8859-1")
        table = soup.find("table", id="tblDadosAjustes")

        if not table:
            print(f"Table 'tblDadosAjustes' not found for date {date_str}.")
            return

        headers = [header.text.strip() for header in table.find_all("th")]
        rows = []
        current_mercadoria = ""  # Keep track of the current commodity

        for row in table.find_all("tr")[1:]:  # Skip header row
            cells = row.find_all("td")
            if len(cells) == len(headers):
                row_data = {
                    headers[i]: cells[i].text.strip() for i in range(len(headers))
                }

                # Update current_mercadoria if we find a non-empty value
                if row_data.get("Mercadoria"):
                    current_mercadoria = row_data["Mercadoria"]
                else:
                    # Fill in empty Mercadoria with the last known value
                    row_data["Mercadoria"] = current_mercadoria

                # Build Ticker: take the first part of Mercadoria before '-' and
                # concatenate with Vencimento. Remove any spaces from the result.
                merc = row_data.get("Mercadoria", "")
                prefix = merc.split("-", 1)[0].strip() if merc else ""
                venc = row_data.get("Vencimento", "")
                row_data["Ticker"] = f"{prefix}{venc}".replace(" ", "")

                rows.append(row_data)

        return rows

    except httpx.RequestError as exc:
        print(f"An error occurred while requesting {exc.request.url!r}.")
    except httpx.HTTPStatusError as exc:
        print(
            f"Error response {exc.response.status_code} while requesting {exc.request.url!r}."
        )


if __name__ == "__main__":
    # To install the required libraries, run:
    # pip install httpx beautifulsoup4 lxml
    import argparse
    import csv
    import sys
    import codecs
    import time

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
        print("Error: Date must be in DD/MM/YYYY format")
        exit(1)

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
        exit(1)

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
            exit(1)

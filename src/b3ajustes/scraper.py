import httpx
from bs4 import BeautifulSoup
from datetime import timedelta


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

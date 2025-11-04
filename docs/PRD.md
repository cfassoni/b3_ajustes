# B3 Ajustes Scraper - Product Requirements Document

## Overview
A command-line tool to scrape and process B3 (BMF Bovespa) settlement prices ("ajustes do pregão"), offering flexible data retrieval and output options.

## Core Features

### Data Retrieval
- [x] Fetch settlement prices from B3's website for a specified date
- [x] Handle ISO-8859-1 encoding from the source website
- [x] Process HTML tables with BeautifulSoup
- [x] Fill empty "Mercadoria" fields with the last known value from the group

### Date Handling
- [x] Accept date input in DD/MM/YYYY format
- [x] Support multi-day data retrieval
- [x] Skip weekends (non-business days) automatically
- [x] Allow both forward and backward date processing
- [x] Rate limiting between requests (configurable delay)

### Data Processing
- [x] Generate Ticker field by:
  - Extracting prefix from Mercadoria (text before first "-")
  - Concatenating with Vencimento
  - Removing all spaces
- [x] Maintain consistent data structure across all records
- [x] Add date field to each record

### Output Formats

#### JSON Output
- [x] Optional JSON output to stdout (`-j/--json` flag)
- [x] UTF-8 encoded JSON
- [x] Pretty-printed with 2-space indentation
- [x] Handle special characters correctly

#### CSV Output
- [x] Optional CSV file output (`-f` parameter)
- [x] ISO-8859-1 encoding for Excel compatibility
- [x] Semicolon (;) as field delimiter
- [x] Consistent column ordering:
  1. Data (Date)
  2. Ticker
  3. Remaining fields

### Command Line Interface
- [x] Required Parameters:
  - Date (DD/MM/YYYY format)
- [x] Optional Parameters:
  - `-f, --file`: CSV output file path
  - `-d, --days`: Number of business days to process (default: 1)
  - `-b, --backward`: Process dates backward (default: forward)
  - `-j, --json`: Enable JSON output (default: off)
  - `--delay`: Seconds between requests (default: 1.0)

### Error Handling
- [x] Validate date format
- [x] Handle HTTP request errors
- [x] Handle missing data gracefully
- [x] Provide clear error messages
- [x] Handle file writing errors

## Technical Requirements

### Dependencies
- Python 3.8+
- External libraries:
  - httpx: For HTTP requests
  - beautifulsoup4: For HTML parsing
  - lxml: For HTML parsing performance

### Encoding Requirements
- Input: Handle ISO-8859-1 from B3's website
- Processing: Convert to UTF-8 for internal processing
- Output:
  - JSON: UTF-8
  - CSV: ISO-8859-1 for Excel compatibility

### Performance Considerations
- Rate limiting to prevent server overload
- Efficient HTML parsing with lxml
- Skip weekends to optimize multi-day retrieval

## Future Considerations
Potential enhancements that could be added:
- Dynamic encoding detection from server responses
- More robust Ticker generation rules
- Unit tests for data processing
- Caching for frequently accessed dates
- Progress bar for multi-day operations
- Parallel request support for faster multi-day retrieval
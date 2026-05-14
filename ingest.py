import requests
import json
import datetime
from datetime import datetime  
from datetime import date
from pathlib import Path
import os
import time

url = 'https://api.fiscaldata.treasury.gov/services/api/fiscal_service/v2/accounting/od/debt_to_penny'
PAGE_SIZE = 10000  # Treasury's max per request
REQUEST_DELAY_SEC = 0.5  # Polite rate limiting for government API

def fetch_all_pages(base_url = url, page_size = PAGE_SIZE, REQUEST_DELAY_SEC = REQUEST_DELAY_SEC):
    """
    Fetches all records from a paginated Treasury Fiscal Data endpoint.
    Uses meta.total-pages to know when to stop; stops on empty response if metadata is missing.
    """

    all_records = []
    page_number = 1
    total_pages = None  # Set on first response

    while True:
        params = {
            'page[size]': page_size,
            'page[number]': page_number,
            'sort': '-record_date'
        }

        response = requests.get(base_url, params=params)
        response.raise_for_status()
        payload = response.json()

        records = payload.get('data', [])
        if not records:
            break

        all_records.extend(records)

        # Extract pagination info on first iteration
        if total_pages is None:
            meta = payload.get('meta', {})
            total_pages = meta.get('total-pages', 1)
            total_count = meta.get('total-count', '?')
            print(f"Total to fetch: {total_count} records across {total_pages} pages")

        print(f"Page {page_number}/{total_pages}: {len(records)} records (running total: {len(all_records)})")

        if page_number >= total_pages:
            break

        page_number += 1
        time.sleep(REQUEST_DELAY_SEC)

    return all_records

def save_raw(records, output_dir):
    """Save the full record list to a timestamped raw JSON file."""
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, 'treasury_raw.json')

    with open(output_path, 'w') as f:
        json.dump({'data': records}, f) # Wrap in {'data': [...]} envelope to match original API shape. This means downstream code that does raw['data'] keeps working


    print(f"Saved {len(records)} records to {output_path}")
    return output_path



def main():
    today = datetime.now().strftime('%Y%m%d')
    output_dir = f'./data/raw/debt_to_penny_{today}' # Preserves a record of each ingestion using the date

    print(f"Fetching from {url}")
    records = fetch_all_pages(url)

    save_raw(records, output_dir)

    print(f"Done. Total records: {len(records)}")


if __name__ == "__main__":
    main()
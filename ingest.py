import requests
import json
from datetime import date
from pathlib import Path

def grab_data():
    url = 'https://api.fiscaldata.treasury.gov/services/api/fiscal_service/v2/accounting/od/debt_to_penny'
    response = requests.get(url)
    data = response.json()
    # with open('debt_to_penny_YYYYMMDD.json', 'w') as file:
    #     json.dump(data, file)


    out_dir = Path("data/raw/debt_to_penny_20260512")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{date.today().isoformat()}.json"
    out_path.write_text(json.dumps(data, indent=2))
    print(f"Saved to {out_path}")


grab_data()
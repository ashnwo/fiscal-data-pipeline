from ingest import url, PAGE_SIZE, REQUEST_DELAY_SEC, fetch_all_pages
from s3 import land_raw, RAW_BUCKET
from transform import transform


raw_response = fetch_all_pages(url, PAGE_SIZE, REQUEST_DELAY_SEC) 
key = land_raw(raw_response)                   
input_uri = f"s3a://{RAW_BUCKET}/{key}"         
df = transform(input_uri)                    



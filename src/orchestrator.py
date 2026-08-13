from ingest import url, PAGE_SIZE, REQUEST_DELAY_SEC, main
from s3 import land_raw, RAW_BUCKET
from transform import transform


raw_response = main() # Fetches data from API
key = land_raw(raw_response)                   # Sends timestamped JSON to S3 (raw zone)
input_uri = f"s3a://{RAW_BUCKET}/{key}"         # Builds url 
df = transform(input_uri)                    # Grabs raw JSON, transfroms file to parquet


